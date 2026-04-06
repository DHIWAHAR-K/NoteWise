"""Persisted scribe visit history (transcript + SOAP). Stored in MongoDB. Do not log bodies."""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import mongo
from app.auth.deps import get_current_user
from app.db.models import User

router = APIRouter(prefix="/scribe", tags=["scribe"])

MAX_TRANSCRIPT_LEN = 500_000


class SOAPIn(BaseModel):
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: str = ""
    citations: list[str] | None = None


class ScribeSessionCreate(BaseModel):
    transcript: str = Field(..., max_length=MAX_TRANSCRIPT_LEN)
    soap: SOAPIn | None = None
    linkedConversationId: str | None = Field(default=None, max_length=64)


class ScribeSessionSummary(BaseModel):
    id: str
    createdAt: int
    updatedAt: int
    linkedConversationId: str | None = None


class ScribeSessionOut(BaseModel):
    id: str
    transcript: str
    soap: dict[str, Any] | None = None
    linkedConversationId: str | None = None
    createdAt: int
    updatedAt: int


def _require_mongo() -> None:
    if not mongo.is_configured():
        raise HTTPException(status_code=503, detail="Scribe storage not configured")


@router.get("/sessions", response_model=list[ScribeSessionSummary])
async def list_sessions(user: User = Depends(get_current_user)):
    _require_mongo()
    db = mongo.get_db()
    uid = str(user.id)
    cursor = (
        db.scribe_sessions.find({"userId": uid}, {"transcript": 0, "soap": 0})
        .sort("createdAt", -1)
        .limit(200)
    )
    out: list[ScribeSessionSummary] = []
    async for doc in cursor:
        out.append(
            ScribeSessionSummary(
                id=doc["_id"],
                createdAt=doc["createdAt"],
                updatedAt=doc["updatedAt"],
                linkedConversationId=doc.get("linkedConversationId"),
            )
        )
    return out


@router.post("/sessions", response_model=ScribeSessionOut)
async def create_session(body: ScribeSessionCreate, user: User = Depends(get_current_user)):
    _require_mongo()
    db = mongo.get_db()
    sid = str(uuid.uuid4())
    now = int(time.time() * 1000)
    uid = str(user.id)
    soap_dict: dict[str, Any] | None = None
    if body.soap is not None:
        soap_dict = body.soap.model_dump()
    doc = {
        "_id": sid,
        "userId": uid,
        "transcript": body.transcript,
        "soap": soap_dict,
        "linkedConversationId": body.linkedConversationId,
        "createdAt": now,
        "updatedAt": now,
    }
    await db.scribe_sessions.insert_one(doc)
    return ScribeSessionOut(
        id=sid,
        transcript=body.transcript,
        soap=soap_dict,
        linkedConversationId=body.linkedConversationId,
        createdAt=now,
        updatedAt=now,
    )


@router.get("/sessions/{session_id}", response_model=ScribeSessionOut)
async def get_session(session_id: str, user: User = Depends(get_current_user)):
    _require_mongo()
    db = mongo.get_db()
    uid = str(user.id)
    doc = await db.scribe_sessions.find_one({"_id": session_id, "userId": uid})
    if not doc:
        raise HTTPException(status_code=404, detail="Session not found")
    return ScribeSessionOut(
        id=doc["_id"],
        transcript=doc["transcript"],
        soap=doc.get("soap"),
        linkedConversationId=doc.get("linkedConversationId"),
        createdAt=doc["createdAt"],
        updatedAt=doc["updatedAt"],
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: User = Depends(get_current_user)):
    _require_mongo()
    db = mongo.get_db()
    uid = str(user.id)
    result = await db.scribe_sessions.delete_one({"_id": session_id, "userId": uid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}
