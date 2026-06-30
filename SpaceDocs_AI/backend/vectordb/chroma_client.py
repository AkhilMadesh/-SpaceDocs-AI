"""
backend/vectordb/chroma_client.py

PHASE 7 — ChromaDB

Purpose:
    Store chunk embeddings persistently and perform fast similarity search
    ("vector search") at query time.

What is a vector database (beginner explanation)?
    A normal database finds rows by EXACT match (e.g. WHERE filename = 'x').
    A vector database finds rows by SIMILARITY — "give me the 5 chunks whose
    meaning is closest to this question's meaning." It does this by comparing
    the distance between embedding vectors in high-dimensional space.

Why ChromaDB specifically:
    - Free, open-source, runs locally — no cloud account needed.
    - Persists to disk automatically (./vectordb folder) — survives app restarts.
    - Simple Python API, perfect for a 5-week internship timeline.

Metadata stored per chunk:
    filename, page number, chunk id, document id
    -> This is what powers citations in Phase 9 ("Source: report.pdf, Page 12").
"""

import os

import chromadb
from chromadb.config import Settings

from backend.chunking.chunker import Chunk
from backend.embeddings.embedder import embed_texts

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./vectordb")
COLLECTION_NAME = "spacedocs_chunks"


def get_client() -> chromadb.Client:
    """
    Create (or connect to) a persistent ChromaDB client.

    PersistentClient writes to disk at PERSIST_DIR, so your vector store
    survives between app restarts — you don't need to re-embed documents
    every time you launch Streamlit.
    """
    return chromadb.PersistentClient(
        path=PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )


def get_collection():
    """
    Get or create the single collection SpaceDocs AI uses to store all chunks.

    A "collection" in ChromaDB is roughly like a table in SQL — a named
    group of vectors + metadata you query together.
    """
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for semantic search
    )


def add_chunks(chunks: list[Chunk]) -> int:
    """
    Embed and store a list of Chunks in ChromaDB.

    Args:
        chunks: output of chunker.chunk_document()

    Returns:
        Number of chunks successfully added.
    """
    if not chunks:
        return 0

    collection = get_collection()

    texts = [c.text for c in chunks]
    embeddings = embed_texts(texts)

    ids = [c.chunk_id for c in chunks]
    metadatas = [
        {
            "filename": c.filename,
            "page_number": c.page_number,
            "chunk_index": c.chunk_index,
            "document_id": c.document_id,
        }
        for c in chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    return len(chunks)


def delete_document(document_id: str) -> None:
    """Remove all chunks belonging to a specific document (used when deleting a PDF)."""
    collection = get_collection()
    collection.delete(where={"document_id": document_id})


def count_chunks() -> int:
    """Return total number of chunks currently stored (useful for sidebar stats)."""
    collection = get_collection()
    return collection.count()


def reset_collection() -> None:
    """Wipe the entire vector store. Use with caution — mainly for testing."""
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # collection may not exist yet


if __name__ == "__main__":
    # Quick manual test — run with: python -m backend.vectordb.chroma_client
    print(f"Persist directory: {PERSIST_DIR}")
    print(f"Current chunk count in store: {count_chunks()}")
