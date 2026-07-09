# 🛰️ SpaceDocs AI

> Talk to NASA, ISRO, and space research documents — in plain English.

**Problem statement:** I2 — Document Q&A (RAG over a Focused Corpus)
**Segment:** Foundations of Applied Machine Learning · B.Tech CSE-AIDE, LPU
**Student:** Akhil | **Cohort:** 2nd Year, 2026

---

## 1. Demo

> *(Add your Loom link here after recording the Week 4 walkthrough)*

[![Live App](https://img.shields.io/badge/🚀_Live_App-Streamlit_Cloud-FF4B4B?style=for-the-badge)](https://your-app-url.streamlit.app)
[![Watch Demo](https://img.shields.io/badge/▶️_Watch_Demo-Loom-7B68EE?style=for-the-badge)](https://www.loom.com/share/your-video-id)

*Live deployment and Loom link added in Week 4.*

---

## 2. Problem Statement

Scientific and aerospace literature — NASA technical reports, ISRO mission
documentation, Chandrayaan and Artemis documents, satellite engineering
manuals — is information-dense, jargon-heavy, and slow to navigate.
A researcher or student often spends more time *finding* an answer inside a
PDF than *understanding* it. Keyword search (Ctrl+F) breaks down when you
don't know the exact term the author used. Generic LLMs hallucinate
plausible-sounding answers about niche aerospace topics they weren't
reliably trained on.

**SpaceDocs AI** solves this by letting users upload space-domain PDFs and
ask questions in plain English, getting back grounded answers with
page-level citations — and an honest "I don't know based on uploaded
documents." when the corpus doesn't contain the answer. Every answer is
traceable to the exact page it came from.

---

## 3. Architecture

```
┌────────────────────────────────────────────────────────┐
│                   INGESTION (offline)                  │
│                                                        │
│  PDF Upload → PyMuPDF Parse → Chunk (500/100 chars)   │
│            → Embed (BGE-small-en-v1.5, local)         │
│            → Store in ChromaDB (persisted to disk)    │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│               QUERY TIME (per question)                │
│                                                        │
│  Question → Embed Query → Hybrid Retrieve (top-5)     │
│             [Dense (ChromaDB) × 0.6]                  │
│           + [BM25 keyword    × 0.4]                   │
│           → Guardrail check (similarity threshold)    │
│           → Gemini 2.5 Flash (grounded prompt)        │
│           → Answer + Citations + Confidence           │
│           → Streamlit Chat UI                         │
└────────────────────────────────────────────────────────┘
```

*See `docs/architecture-diagram.md` for the Mermaid source.*

---

## 4. Tech Stack

| Component | Choice | Why |
|---|---|---|
| **PDF parsing** | PyMuPDF | Fast, accurate, gives per-page text for citations |
| **Chunking** | LangChain `RecursiveCharacterTextSplitter` | Paragraph-aware splitting, predictable behaviour |
| **Embeddings** | `BAAI/bge-small-en-v1.5` (local, via `sentence-transformers`) | Free, offline, strong retrieval benchmarks for its size |
| **Vector DB** | ChromaDB (`PersistentClient`) | Zero-setup, persists to disk, native metadata filtering |
| **Keyword search** | `rank-bm25` | Lightweight BM25 for the hybrid retrieval requirement |
| **LLM** | Gemini 2.5 Flash | Free tier, fast, follows strict grounding instructions |
| **UI** | Streamlit | Fastest path to a usable, demo-able interface |
| **Language** | Python 3.11 | Internship track standard |

---

## 5. Quickstart

### Prerequisites
- Python 3.11
- A free Gemini API key: https://aistudio.google.com/app/apikey

### Install

```bash
git clone https://github.com/<your-username>/SpaceDocs_AI.git
cd SpaceDocs_AI

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Open .env and paste your GOOGLE_API_KEY
```

### Run

```bash
streamlit run app/main.py
```

App available at `http://localhost:8501`.

Upload PDFs in the sidebar → ask questions in the chat → compare two
documents in the **Compare** tab.

### Test

```bash
pytest tests/ -v
```

Expected: all tests pass. Tests run without any API keys or services.

### Test the data layer directly (no UI needed)

```bash
# Parse a PDF and print the first page
python -m backend.ingestion.pdf_loader data/uploads/your_report.pdf

# Run hybrid retrieval (requires ingested docs in ChromaDB)
python -m backend.retrieval.retriever "What is PSLV?"

# Full Q&A pipeline (requires GOOGLE_API_KEY)
python -m backend.llm.gemini_client "Explain the Chandrayaan-3 landing"
```

---

## 6. Data Sources

User-uploaded PDFs — nothing is bundled in the repo. Recommended corpus
for testing and demo:

| Document | Source |
|---|---|
| Chandrayaan-3 Mission Overview | ISRO public releases |
| Artemis Program Mission Report | NASA.gov |
| PSLV User's Manual | ISRO/Antrix |
| Satellite Engineering Handbook | Public domain / open access |
| NASA CubeSat Launch Initiative Guide | NASA.gov |

All documents are freely and publicly available. Upload them via the
Streamlit sidebar to populate the knowledge base.

---

## 7. ADRs

Three architecture decision records explaining the key technical choices:

| ADR | Decision | TL;DR |
|---|---|---|
| [ADR-001](docs/adr/ADR-001-vector-database-choice.md) | Vector database | ChromaDB: free, local, zero-setup, sufficient for this corpus size |
| [ADR-002](docs/adr/ADR-002-embedding-model-choice.md) | Embedding model | BGE-small-en-v1.5: best retrieval quality for its size, runs offline |
| [ADR-003](docs/adr/ADR-003-guardrail-strategy.md) | Guardrail strategy | Two layers: similarity threshold + prompt instruction |

---

## 8. Mini-Extension — Compare Two Documents

**What:** Upload two PDFs (e.g., Chandrayaan-3 report and Artemis mission
report), select them in the **Compare** tab, and ask any comparison
question:
- *"What's different between these on propulsion technology?"*
- *"How do their mission objectives compare?"*
- *"Which document covers lunar south pole landing in more detail?"*

**How it works:**
1. Fetch a representative sample of chunks from each document independently
   (via ChromaDB metadata filter on `document_id`).
2. Pass both chunk sets to Gemini 2.5 Flash with a comparison-focused
   prompt that strictly prohibits outside knowledge.
3. If the excerpts don't support a confident comparison on some aspect,
   the model is instructed to say so explicitly rather than guessing.

**Why it matters:** multi-document reasoning is a step up from single-doc
RAG. It mirrors a real aerospace analyst workflow — "how does this ISRO
mission differ from NASA's approach?" — and is the direct precursor to the
3rd year "enterprise messy corpus" extension.

**Code:** `backend/llm/doc_comparator.py` + `frontend/features.py` (Compare tab)

---

## 9. Known Limitations

- **Scanned/image-only PDFs** are not supported — PyMuPDF extracts text
  only, no OCR. Clear error message is shown.
- **0.35 confidence threshold** is manually tuned, not calibrated against
  real eval data yet. Tuning happens in Week 3-4 once eval questions are
  scored.
- **BM25 index is rebuilt per-query** from the ChromaDB candidate pool —
  fine for the corpus size here, not ideal at scale.
- **Single-language only** — English documents. Non-English PDFs produce
  garbled text from PyMuPDF's text extractor.
- **No multi-user isolation** — one shared ChromaDB instance. Uploading
  different users' documents would intermix unless filtered by `document_id`.

---

## 10. What I'd Do in 3rd Year

See the full roadmap: [`docs/roadmap_3rd_year.md`](docs/roadmap_3rd_year.md)

Short version:
1. **Aug-Sep 2026:** Add the evaluation harness (20+ Q&A pairs, RAGAS
   metrics), tune the confidence threshold, add hybrid retrieval reranker.
2. **Oct-Nov 2026:** Migrate from ChromaDB to Qdrant Cloud; add multi-format
   ingestion (Word, HTML, tables); proper CI/CD with GitHub Actions.
3. **Nov-Dec 2026:** Add an agentic multi-step query layer — for complex
   questions that need multiple retrievals before answering.
4. **3rd year internship (2027):** This becomes the I3/E3 corpus-at-scale
   problem — same RAG architecture, but over 4+ source types, dirty data,
   fine-tuned domain embedding, continuous eval harness.

---

## 11. License & Acknowledgements

**License:** MIT — see [LICENSE](LICENSE)

**Acknowledgements:**
- NASA and ISRO for publicly available mission documentation
- `sentence-transformers` / BAAI for the BGE embedding model
- LangChain, ChromaDB, rank-bm25 open-source communities
- Google Gemini API free tier
- LPU internship mentors for the I2 problem design

---

## Week 3 Progress Notes

**What I'd do differently:**
I under-estimated how much the retriever matters relative to the LLM. I
spent a lot of Week 2 thinking about the Gemini prompt and almost none
thinking about retrieval quality. In hindsight, I would have built the
hybrid BM25 + dense retriever first and validated it with test questions
before writing a single line of Gemini integration — because bad retrieval
makes good prompting useless, but good retrieval makes even a mediocre
prompt produce reasonable answers.

**Status one-pager:**
- **Done:** hybrid retrieval, mini-extension (Compare Two Documents), ADR-002
  and ADR-003, all deprecated SDK calls fixed, full test suite (5 test files),
  Milestone 1 README complete.
- **Stuck:** nothing blocking. Confidence threshold is still a guess —
  needs real eval data to tune (next).
- **3 goals for Week 4:** (1) deploy to Streamlit Cloud, (2) record 3-min
  Loom walkthrough, (3) write 20+ eval questions and run first scored pass.
- **Mentor help needed:** advice on whether to use RAGAS or a simpler
  hand-rolled eval (LLM-as-judge) for the 20-question scored pass — which
  is more defensible in a placement interview?
