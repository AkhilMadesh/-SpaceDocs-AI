# SpaceDocs AI — Design Doc

**Problem statement:** I2 — Document Q&A (RAG over a Focused Corpus)
**Segment:** Foundations of Applied Machine Learning
**Author:** Akhil

## What I'm building
**SpaceDocs AI** — a "talk to your space documents" tool. Upload NASA/ISRO
mission reports, Chandrayaan/Artemis documentation, or satellite
engineering manuals as PDFs, ask questions in plain English, get back
grounded answers with page-number citations — and an honest "I don't know"
when the uploaded documents don't actually contain the answer.

## Corpus
Space-domain PDFs of my choosing: NASA technical reports, ISRO mission
documentation (Chandrayaan, PSLV), Artemis program reports, satellite
engineering manuals. Roughly 5-10 PDFs to start (Week 1-2), with the
option to grow toward the ~30-40 PDF target later in the build.

## Tech Stack

| Component | Choice | Why (one line) |
|---|---|---|
| PDF parsing | PyMuPDF | Fast, accurate text extraction, gives per-page access for citations |
| Chunking | LangChain `RecursiveCharacterTextSplitter` | Paragraph-aware splitting, predictable behavior |
| Embeddings | BAAI/bge-small-en-v1.5 (local) | Free, runs offline, no API key, strong small-model retrieval |
| Vector DB | ChromaDB | Zero-setup, persists to disk, native metadata filtering |
| LLM | Gemini 2.5 Flash | Free tier, fast, follows strict grounding instructions well |
| UI | Streamlit | Fastest path to a usable, demo-able interface |

## Architecture (text form for Week 1; diagram in `docs/architecture-diagram.md`)
```
PDF upload -> PyMuPDF parse -> chunk (500/100) -> embed (BGE-small)
           -> store in ChromaDB
User question -> embed query -> semantic retrieve (top-5)
              -> guardrail check (confidence threshold)
              -> Gemini 2.5 Flash (grounded prompt) -> answer + citations
              -> Streamlit chat UI
```

## Guardrails
- If the best retrieved chunk's similarity score is below 0.35, skip the
  LLM call entirely and return "I don't know based on uploaded documents."
- The system prompt also instructs Gemini to return that exact sentence if
  retrieved context doesn't actually answer the question, even when
  retrieval technically returned chunks.

## What's explicitly OUT of scope for Week 1-2
- Compare Two Documents (mini-extension — Week 3)
- Document summarization and quiz generation (also Week 3+ additions, not
  required for the skinny build)
- Full RAGAS eval report with 20+ scored Q&A pairs (Week 3-4)
- Live deployment (Week 4)
- Multiple ADRs (only ADR-001 exists at Week 2 — 2 more land Week 3)

## Open questions for mentor review
- Is BGE-small good enough for technical aerospace vocabulary, or should I
  benchmark it against a domain-adjacent model?
- Is a 0.35 confidence threshold reasonable for an out-of-domain guardrail,
  or too strict/loose? No eval data exists yet to tune it against —
  revisiting once eval questions are written (Week 3-4).
