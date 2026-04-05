"""RAG service: retrieve top-k chunks from Pinecone via LangChain."""
import os
from functools import lru_cache
from typing import Any

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


@lru_cache(maxsize=1)
def _vector_store() -> PineconeVectorStore:
    api_key = os.environ["PINECONE_API_KEY"]
    index_name = os.environ["PINECONE_INDEX_NAME"]
    pc = Pinecone(api_key=api_key)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return PineconeVectorStore(index=pc.Index(index_name), embedding=embeddings)


def retrieve(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Return top-k chunks with text and citation metadata."""
    store = _vector_store()
    docs = store.similarity_search(query, k=top_k)
    return [
        {
            "text": doc.page_content,
            "source": doc.metadata.get("source_id", "unknown"),
            "title": doc.metadata.get("title", ""),
        }
        for doc in docs
    ]
