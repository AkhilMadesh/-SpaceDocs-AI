# SpaceDocs AI — Design Document

## 1. Overview

SpaceDocs AI is a Retrieval-Augmented Generation (RAG) system that allows
users to upload space-research PDFs (NASA, ISRO, Chandrayaan, Artemis,
satellite engineering manuals) and ask natural-language questions, receiving
answers grounded in and cited from the uploaded content.

## 2. Goals

- Accurate, citation-backed answers from user-uploaded documents only.
- Clear refusal ("I don't know based on uploaded documents.") when content
  is insufficient or out-of-domain.
- Beginner-buildable within a 5-week internship timeline using free tools.
- Deployable to Streamlit Community Cloud with no paid infrastructure.

## 3. Non-Goals

- Real-time multi-user concurrent editing of the same document set.
- OCR for scanned/image-only PDFs (documented as a future improvement).
- Support for non-English documents in the initial version.

## 4. System Architecture

```
User → Streamlit UI → Ingestion Pipeline → ChromaDB (vector store)
                                  ↓
                      Retriever ← (query embedding)
                                  ↓
                         Gemini 2.5 Flash (grounded generation)
                                  ↓
                      Answer + Citations + Confidence → UI
```

See `app/main.py`, `frontend/`, and `backend/` for the corresponding code
modules at each stage.

## 5. Data Flow

1. User uploads PDF(s) via Streamlit sidebar (`frontend/sidebar.py`).
2. `backend/ingestion/pipeline.py` orchestrates: save to disk → parse
   (`pdf_loader.py`) → chunk (`chunker.py`) → embed + store
   (`embedder.py` + `chroma_client.py`).
3. User asks a question via chat input (`frontend/chat.py`).
4. `backend/retrieval/retriever.py` embeds the query and retrieves top-k
   similar chunks from ChromaDB.
5. `backend/llm/gemini_client.py` applies the out-of-domain guardrail, then
   (if passed) constructs a grounded prompt and calls Gemini 2.5 Flash.
6. Answer, citations, and confidence score are returned to the UI and
   appended to `st.session_state.chat_history`.

## 6. Key Design Decisions

See `docs/ADR-001` through `docs/ADR-003` for vector database, embedding
model, and guardrail strategy decisions respectively.

## 7. Module Responsibilities

| Module | Responsibility |
|---|---|
| `backend/ingestion/` | File handling, PDF parsing, metadata tracking |
| `backend/chunking/` | Splitting text into retrievable units |
| `backend/embeddings/` | Text → vector conversion |
| `backend/vectordb/` | Vector storage and persistence (ChromaDB) |
| `backend/retrieval/` | Query embedding + similarity search |
| `backend/llm/` | Prompting, grounding, guardrails, summarization, quiz, comparison |
| `frontend/` | Streamlit UI components |
| `app/` | Application entry point |
| `evaluation/` | Test questions, RAGAS scoring, manual hallucination checks |

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Hallucinated answers | Two-layer guardrail (ADR-003) |
| Scanned PDFs produce no text | Explicit `ValueError` raised with clear message; documented as a known limitation |
| API key exposure | `.env` gitignored from Phase 1; `.env.example` provided instead |
| Vector store growing unbounded | `delete_document()` available; document-level deletion wired into sidebar |
| Embedding/LLM model lock-in | All model access wrapped behind small function interfaces, swappable via `.env` |

## 9. Future Work

See "Future Improvements" and "Third-Year Extension Roadmap" in `README.md`.
