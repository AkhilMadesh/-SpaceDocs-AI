"""
backend/embeddings/embedder.py

PHASE 6 — Embeddings

Purpose:
    Convert text chunks into dense numerical vectors ("embeddings") that
    capture SEMANTIC MEANING, not just keywords.

What is an embedding (beginner explanation)?
    Imagine plotting every sentence as a point in space. Sentences with
    similar MEANING land close together, even if they share zero words.
    e.g. "The rocket launched successfully" and "The mission lift-off was a
    success" would land near each other, despite having different words.

Why semantic similarity matters for RAG:
    A user might ask "How does PSLV work?" but the document says
    "Polar Satellite Launch Vehicle architecture" — no exact keyword match,
    but semantically nearly identical. Keyword search would miss this;
    embedding-based search finds it easily.

Model used: BAAI/bge-small-en-v1.5 (via sentence-transformers)
    - Free, open-source, runs locally (no API key, no per-call cost).
    - 384-dimensional vectors — small enough to be fast, accurate enough
      for technical document retrieval.
    - Alternative: all-MiniLM-L6-v2 (even smaller/faster, slightly less accurate).
"""

import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model ONCE and cache it.

    Why caching matters:
        Loading a transformer model from disk takes a few seconds. Without
        caching, every single chunk embedding call would reload the model —
        making ingestion painfully slow. @lru_cache ensures this function
        body only runs once per app session.
    """
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a batch of text strings.

    Args:
        texts: list of chunk text strings.

    Returns:
        List of embedding vectors (list of floats), one per input text.
    """
    model = get_embedding_model()
    # normalize_embeddings=True makes cosine-similarity search more reliable
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """
    Generate a single embedding for a user's question.

    Note: BGE models recommend prefixing QUERIES (not documents) with an
    instruction for best retrieval accuracy.
    """
    instructed_query = f"Represent this sentence for searching relevant passages: {query}"
    return embed_texts([instructed_query])[0]


def get_embedding_dimension() -> int:
    """Return the vector dimensionality of the loaded model (e.g. 384)."""
    model = get_embedding_model()
    return model.get_sentence_embedding_dimension()


if __name__ == "__main__":
    # Quick manual test — run with: python -m backend.embeddings.embedder
    sample_texts = [
        "The PSLV is a four-stage launch vehicle developed by ISRO.",
        "Chandrayaan-3 successfully landed near the lunar south pole.",
    ]
    vectors = embed_texts(sample_texts)

    print(f"Embedding model: {EMBEDDING_MODEL_NAME}")
    print(f"Vector dimension: {get_embedding_dimension()}")
    print(f"Generated {len(vectors)} embeddings")
    print(f"First 5 values of embedding 1: {vectors[0][:5]}")
