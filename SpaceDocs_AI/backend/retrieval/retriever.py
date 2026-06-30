"""
backend/retrieval/retriever.py

PHASE 8 — Retriever

Purpose:
    Take a user's question, embed it, and search ChromaDB for the TOP_K
    most semantically similar chunks. This is the "R" in RAG.

Why TOP_K = 5 by default?
    - Too few (e.g. 1-2): risk missing relevant context spread across chunks.
    - Too many (e.g. 20+): floods the LLM prompt with noise, increases cost,
      and can dilute the model's focus on the truly relevant passages.
    - 5 is a well-tested sweet spot for short-to-medium technical documents.
"""

import os
from dataclasses import dataclass

from backend.embeddings.embedder import embed_query
from backend.vectordb.chroma_client import get_collection

TOP_K = int(os.getenv("TOP_K_RETRIEVAL", 5))


@dataclass
class RetrievedChunk:
    """A single retrieved chunk with its similarity score and citation metadata."""
    text: str
    filename: str
    page_number: int
    chunk_index: int
    similarity_score: float  # 0.0 (unrelated) to 1.0 (identical meaning)


def retrieve(query: str, top_k: int = TOP_K, document_filter: str | None = None) -> list[RetrievedChunk]:
    """
    Retrieve the most relevant chunks for a given query.

    Args:
        query: the user's natural-language question.
        top_k: how many chunks to retrieve.
        document_filter: optional document_id to restrict search to one document
                          (used by the "compare two documents" feature in Phase 12).

    Returns:
        List of RetrievedChunk, sorted by relevance (most relevant first).
    """
    collection = get_collection()
    query_embedding = embed_query(query)

    where_clause = {"document_id": document_filter} if document_filter else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause,
    )

    retrieved: list[RetrievedChunk] = []

    # ChromaDB returns results nested in lists (one list per query embedding)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]  # cosine DISTANCE (lower = more similar)

    for text, meta, distance in zip(documents, metadatas, distances):
        # Convert cosine distance -> similarity score (0 to 1, higher = better)
        similarity = round(1 - distance, 4)

        retrieved.append(
            RetrievedChunk(
                text=text,
                filename=meta["filename"],
                page_number=meta["page_number"],
                chunk_index=meta["chunk_index"],
                similarity_score=similarity,
            )
        )

    return retrieved


def format_citations(chunks: list[RetrievedChunk]) -> str:
    """
    Build a human-readable citation block from retrieved chunks.

    Example output:
        Source: chandrayaan3_report.pdf | Page: 12 | Confidence: 0.87
        Source: chandrayaan3_report.pdf | Page: 14 | Confidence: 0.81
    """
    lines = []
    for c in chunks:
        lines.append(
            f"Source: {c.filename} | Page: {c.page_number} | Confidence: {c.similarity_score}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    # Quick manual test — run with: python -m backend.retrieval.retriever "your question"
    import sys

    if len(sys.argv) < 2:
        print('Usage: python -m backend.retrieval.retriever "your question here"')
        sys.exit(1)

    question = sys.argv[1]
    results = retrieve(question)

    print(f"Top {len(results)} results for: '{question}'\n")
    for r in results:
        print(f"[{r.similarity_score}] {r.filename} (p.{r.page_number}) -> {r.text[:150]}...\n")
