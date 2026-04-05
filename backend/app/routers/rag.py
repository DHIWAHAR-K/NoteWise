import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.rag.service import retrieve

router = APIRouter(prefix="/rag", tags=["rag"])


class RAGRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class Chunk(BaseModel):
    text: str
    source: str
    title: str


class RAGResponse(BaseModel):
    chunks: list[Chunk]
    disclaimer: str = "NOT for clinical use."


@router.post("/query", response_model=RAGResponse)
async def rag_query(req: RAGRequest):
    """Retrieve top-k medical knowledge base chunks for a query."""
    pinecone_key = os.getenv("PINECONE_API_KEY", "")
    if not pinecone_key:
        raise HTTPException(status_code=503, detail="PINECONE_API_KEY not configured")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")

    try:
        raw = retrieve(req.query, req.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return RAGResponse(chunks=[Chunk(**c) for c in raw])
