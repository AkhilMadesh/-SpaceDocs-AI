# ADR-001: Choice of Vector Database

## Context
SpaceDocs AI needs to store chunk embeddings (from parsed NASA/ISRO PDFs)
and perform fast similarity search at query time. I needed a vector store
that's free, quick to set up within a 5-week "Foundations" timeline, and
doesn't require a cloud account just to start ingesting documents.
Options considered: ChromaDB, Pinecone, FAISS.

## Decision
I chose **ChromaDB**, run locally with `PersistentClient`, for the Week
1-2 skinny build and the foundation overall.

| Criteria | ChromaDB | Pinecone | FAISS |
|---|---|---|---|
| Cost | Free, local | Free tier, then paid | Free |
| Setup complexity | Very low (`pip install`) | Requires cloud account/API key | Low, but no built-in persistence/metadata filtering |
| Persistence | Built-in (`PersistentClient`) | Cloud-managed | Manual (must implement yourself) |
| Metadata filtering | Native support (`where=`) | Native support | Not native — requires custom indexing |
| Beginner-friendliness | High | Medium | Low |

ChromaDB's zero-cost, zero-account-setup, local-first design was decisive
for a beginner-led, free-tools-preferred, 5-week build. It also persists
to disk automatically, so the vector store survives app restarts without
extra engineering — important for the Week 1 "data layer working" check.

## Consequences
**Positive:** fast to set up, no API keys/billing for the vector store,
works fully offline, sufficient performance for the chunk volumes this
project will hit in 5 weeks (low thousands of chunks, not millions).

**Negative:** doesn't scale horizontally across multiple servers the way a
managed cloud vector DB would. For a production system beyond hundreds of
documents, migration to Pinecone or Qdrant Cloud would be the natural next
step — noted in the 3rd Year Extension Roadmap.

**Mitigation:** all ChromaDB-specific code is isolated behind a small
function interface in `backend/vectordb/chroma_client.py`
(`add_chunks`, `count_chunks`, query via the collection object), so
migrating to another vector DB later only requires rewriting one file, not
touching ingestion, chunking, retrieval, or generation logic.

## Alternatives Considered
- **Pinecone:** rejected for the Week 1-2 build — requires a cloud account
  and API key just to start, adding setup friction that doesn't pay off
  yet at this corpus size. Worth revisiting once the project scales past
  a single-machine local setup.
- **FAISS:** rejected — fast, but has no built-in persistence or metadata
  filtering. I'd have had to hand-roll both, which is unnecessary
  complexity for a Week 1-2 "skinny" build whose whole point is to prove
  the end-to-end flow works, not to optimize the vector store.
