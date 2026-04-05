#!/usr/bin/env python
"""Ingest medical KB markdown files into Pinecone via LangChain.

Usage:
    conda activate notewise
    cd backend
    python scripts/ingest.py [--kb-dir data/kb] [--chunk-size 512] [--chunk-overlap 64]
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec


def load_docs(kb_dir: Path) -> list[Document]:
    docs = []
    for md_file in sorted(kb_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        # Extract source_id and title from last lines if present
        source_id = md_file.stem
        title = md_file.stem.replace("_", " ").title()
        for line in text.splitlines():
            if line.startswith("source_id:"):
                source_id = line.split(":", 1)[1].strip()
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip()
        docs.append(Document(page_content=text, metadata={"source_id": source_id, "title": title}))
    return docs


def main():
    parser = argparse.ArgumentParser(description="Ingest KB docs into Pinecone")
    parser.add_argument("--kb-dir", default="data/kb", help="Directory with .md files")
    parser.add_argument("--chunk-size", type=int, default=512)
    parser.add_argument("--chunk-overlap", type=int, default=64)
    args = parser.parse_args()

    pinecone_key = os.environ.get("PINECONE_API_KEY", "")
    index_name = os.environ.get("PINECONE_INDEX_NAME", "notewise-kb")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    if not pinecone_key or not openai_key:
        sys.exit("ERROR: PINECONE_API_KEY and OPENAI_API_KEY must be set in .env")

    kb_dir = Path(args.kb_dir)
    if not kb_dir.is_dir():
        sys.exit(f"ERROR: KB directory not found: {kb_dir}")

    print(f"Loading documents from {kb_dir}...")
    docs = load_docs(kb_dir)
    print(f"  Loaded {len(docs)} documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    print(f"  Split into {len(chunks)} chunks")

    pc = Pinecone(api_key=pinecone_key)
    if index_name not in [idx.name for idx in pc.list_indexes()]:
        print(f"Creating Pinecone index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
    print("Upserting chunks to Pinecone...")
    PineconeVectorStore.from_documents(chunks, embeddings, index_name=index_name)
    print(f"Done. {len(chunks)} chunks upserted to index '{index_name}'.")


if __name__ == "__main__":
    main()
