"""Chat history stored in MongoDB. Avoid logging request bodies or message content.

Mark 3: conversations are scoped by JWT user (`userId`). Documents without `userId` (pre-Mark-3)
are orphaned and never returned.
"""

from __future__ import annotations

import time
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import mongo
from app.auth.deps import get_current_user
from app.db.models import User

router = APIRouter(prefix="/chat", tags=["chat"])

MAX_CONTENT_LEN = 100_000
MAX_MESSAGES_PER_CONVERSATION = 500

MessageRole = Literal["user", "assistant"]


class ChatMessageIn(BaseModel):
    role: MessageRole
    content: str = Field(..., max_length=MAX_CONTENT_LEN)
    id: str | None = None
    timestamp: int | None = None


class ChatMessageOut(BaseModel):
    id: str
    role: MessageRole
    content: str
    timestamp: int


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class ConversationSummary(BaseModel):
    id: str
    title: str
    updatedAt: int


class ConversationOut(BaseModel):
    id: str
    title: str
    createdAt: int
    updatedAt: int
    messages: list[ChatMessageOut]


def _require_mongo() -> None:
    if not mongo.is_configured():
        raise HTTPException(status_code=503, detail="Chat storage not configured")


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(user: User = Depends(get_current_user)):
    _require_mongo()
    db = mongo.get_db()
    uid = str(user.id)
    cursor = (
        db.conversations.find({"userId": uid}, {"messages": 0})
        .sort("updatedAt", -1)
        .limit(100)
    )
    out: list[ConversationSummary] = []
    async for doc in cursor:
        out.append(
            ConversationSummary(
                id=doc["_id"],
                title=doc.get("title", "Chat"),
                updatedAt=doc["updatedAt"],
            )
        )
    return out


@router.post("/conversations", response_model=ConversationOut)
async def create_conversation(
    user: User = Depends(get_current_user),
    body: ConversationCreate = ConversationCreate(),
):
    _require_mongo()
    db = mongo.get_db()
    cid = str(uuid.uuid4())
    now = int(time.time() * 1000)
    title = (body.title or "New chat").strip() or "New chat"
    uid = str(user.id)
    doc = {
        "_id": cid,
        "userId": uid,
        "title": title,
        "createdAt": now,
        "updatedAt": now,
        "messages": [],
    }
    await db.conversations.insert_one(doc)
    return ConversationOut(
        id=cid,
        title=title,
        createdAt=now,
        updatedAt=now,
        messages=[],
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationOut)
async def get_conversation(conversation_id: str, user: User = Depends(get_current_user)):
    _require_mongo()
    db = mongo.get_db()
    uid = str(user.id)
    doc = await db.conversations.find_one({"_id": conversation_id, "userId": uid})
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = [
        ChatMessageOut(
            id=m["id"],
            role=m["role"],
            content=m["content"],
            timestamp=m["timestamp"],
        )
        for m in doc.get("messages", [])
    ]
    return ConversationOut(
        id=doc["_id"],
        title=doc.get("title", "Chat"),
        createdAt=doc["createdAt"],
        updatedAt=doc["updatedAt"],
        messages=messages,
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ConversationOut,
)
async def append_message(
    conversation_id: str,
    body: ChatMessageIn,
    user: User = Depends(get_current_user),
):
    _require_mongo()
    db = mongo.get_db()
    uid = str(user.id)
    now = body.timestamp if body.timestamp is not None else int(time.time() * 1000)
    msg_id = body.id or str(uuid.uuid4())
    msg = {
        "id": msg_id,
        "role": body.role,
        "content": body.content,
        "timestamp": now,
    }

    count_result = await db.conversations.aggregate(
        [
            {"$match": {"_id": conversation_id, "userId": uid}},
            {"$project": {"n": {"$size": {"$ifNull": ["$messages", []]}}}},
        ]
    ).to_list(1)
    if not count_result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if count_result[0]["n"] >= MAX_MESSAGES_PER_CONVERSATION:
        raise HTTPException(status_code=400, detail="Conversation message limit reached")

    result = await db.conversations.update_one(
        {"_id": conversation_id, "userId": uid},
        {
            "$push": {"messages": msg},
            "$set": {"updatedAt": now},
        },
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return await get_conversation(conversation_id)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user: User = Depends(get_current_user)):
    _require_mongo()
    db = mongo.get_db()
    uid = str(user.id)
    result = await db.conversations.delete_one({"_id": conversation_id, "userId": uid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True}
