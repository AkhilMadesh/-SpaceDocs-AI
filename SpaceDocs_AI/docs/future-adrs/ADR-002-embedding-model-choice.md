# ADR-002: Choice of Embedding Model

**Status:** Accepted
**Date:** 2026-06-27

## Context

We need to convert text chunks into vector embeddings for semantic search.
Candidates: `BAAI/bge-small-en-v1.5`, `all-MiniLM-L6-v2`, OpenAI
`text-embedding-3-small`, Gemini embeddings.

## Decision

We chose **BAAI/bge-small-en-v1.5** (via `sentence-transformers`), running
locally, as the primary embedding model — with `all-MiniLM-L6-v2` documented
as a lighter-weight fallback.

## Rationale

| Criteria | BGE-small-en-v1.5 | MiniLM-L6-v2 | Gemini Embeddings | OpenAI Embeddings |
|---|---|---|---|---|
| Cost | Free, local | Free, local | Free tier via API | Paid per token |
| Dimensions | 384 | 384 | 768 | 1536 |
| Retrieval quality (general benchmarks) | High | Medium | High | High |
| Requires internet/API key | No | No | Yes | Yes |
| Speed (CPU) | Moderate | Fast | N/A (network latency) | N/A (network latency) |

BGE-small was selected because it runs **entirely offline**, has no
per-request cost or rate limits, and benchmarks strongly for retrieval
tasks relative to its small size — a good fit for a student project that
needs to embed ~30-40 PDFs repeatedly during development without incurring
API costs.

## Consequences

- **Positive:** Zero embedding cost, no network dependency during ingestion,
  reproducible results.
- **Negative:** Slightly slower on CPU-only machines for very large batches;
  394-dim vectors carry less semantic nuance than larger models like
  OpenAI's 1536-dim embeddings.
- **Mitigation:** `backend/embeddings/embedder.py` reads the model name from
  an environment variable (`EMBEDDING_MODEL`), so switching to
  `all-MiniLM-L6-v2` or a cloud embedding model later requires only a config
  change, not a code rewrite — provided the new model is also wrapped behind
  the same `embed_texts()`/`embed_query()` interface.
