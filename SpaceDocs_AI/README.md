# 🛰️ SpaceDocs AI

> Talk to NASA, ISRO, and space research documents — in plain English.

**Problem statement code:** I2 — Document Q&A (RAG over a Focused Corpus)
**Segment:** Foundations of Applied Machine Learning
**Student:** Akhil
**Status:** Week 2 — skinny end-to-end build working

---

## What this is (right now)

This is a **Week 1-2 stage build**:

- ✅ Upload PDFs (NASA reports, ISRO mission docs, Chandrayaan/Artemis
  documentation, satellite engineering manuals)
- ✅ They get parsed, chunked, embedded, and stored in a vector database
- ✅ Ask a question, get a grounded answer with page-number citations
- ✅ Out-of-domain guardrail — says "I don't know based on uploaded
  documents" instead of hallucinating
- ✅ Conversation history + confidence scores in the UI

**Not yet built (later weeks, by design — see `02_Technical_Problem_Compendium.md`):**
- ❌ Compare Two Documents (mini-extension — Week 3)
- ❌ Document summarization, quiz generation (later additions, not required for the skinny build)
- ❌ Formal eval report with 20+ scored Q&A pairs (Week 3-4)
- ❌ Live deployment (Week 4)
- ❌ ADR-002 and ADR-003 (drafted ahead of schedule, held in `docs/future-adrs/` until Week 3 per the spec)

---

## Tech Stack

| Component | Choice | Why |
|---|---|---|
| PDF parsing | PyMuPDF | Fast, accurate, gives per-page text for citations |
| Chunking | LangChain `RecursiveCharacterTextSplitter` | Paragraph-aware splitting |
| Embeddings | `BAAI/bge-small-en-v1.5` (local) | Free, offline, strong small-model retrieval |
| Vector DB | ChromaDB | Zero-setup, persists to disk |
| LLM | Gemini 2.5 Flash | Free tier, fast, follows grounding instructions well |
| UI | Streamlit | Fastest path to a demo-able interface |

Full reasoning: [`docs/design_doc.md`](docs/design_doc.md)
First architecture decision record: [`docs/adr/ADR-001-vector-database-choice.md`](docs/adr/ADR-001-vector-database-choice.md)

---

## Architecture

```
PDF upload → PyMuPDF parse → chunk (500/100) → embed (BGE-small)
          → store in ChromaDB

User question → embed query → semantic retrieve (top-5)
             → guardrail check (confidence threshold)
             → Gemini 2.5 Flash (grounded prompt) → answer + citations
             → Streamlit chat UI
```

Diagram source (Mermaid): [`docs/architecture-diagram.md`](docs/architecture-diagram.md)

---

## Quickstart

### Prerequisites
- Python 3.11
- A free Gemini API key: https://aistudio.google.com/app/apikey

### Install

```bash
git clone <your-repo-url>
cd SpaceDocs_AI

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your GOOGLE_API_KEY
```

### Run

```bash
streamlit run app/main.py
```

Open `http://localhost:8501`, upload PDFs in the sidebar, then ask a question.

### Test the data layer directly (no UI)

```bash
# Confirm PDF parsing works
python -m backend.ingestion.pdf_loader data/uploads/your_report.pdf

# Confirm retrieval works (after ingesting via the app)
python -m backend.retrieval.retriever "your test question"

# Confirm full grounded generation works (requires GOOGLE_API_KEY)
python -m backend.llm.gemini_client "your test question"
```

### Run tests

```bash
pytest tests/ -v
```

---

## Data Source

NASA technical reports, ISRO mission documentation (Chandrayaan, PSLV),
Artemis program reports, and satellite engineering manuals — user-uploaded
PDFs, my own selection. Nothing is bundled in the repo; documents are
uploaded by the user at runtime.

---

## What I Learned This Week (Week 2)

- ChromaDB's `PersistentClient` solved a problem I expected to be annoying
  (keeping the vector store alive across app restarts) — it just works.
- Writing the system prompt for the "I don't know" guardrail took more
  iteration than expected — the model would sometimes answer *near* the
  fallback sentence instead of exactly it, which breaks simple string
  matching. Settled on an explicit "respond with EXACTLY this sentence"
  instruction.
- Caught a real bug while reviewing current docs: `google-generativeai` is
  deprecated. Switched the LLM call path to the current `google-genai`
  client SDK before this even got to a mentor review — good habit to keep.

## What Surprised Me

How much the out-of-domain guardrail threshold matters in practice. With
no tuning, 0.35 felt arbitrary on paper, but watching it correctly reject
an off-topic test question ("what's the capital of France?") while still
answering a real Chandrayaan question made the design click — confidence
scoring isn't just a UI nicety, it's load-bearing for trust.

---

## Status One-Pager

**What's done:**
Full skinny pipeline — upload, parse, chunk, embed, store, retrieve,
generate grounded answer, display with citations and confidence. Guardrail
for out-of-domain questions implemented and manually tested. ADR-001
written in the program's required template.

**What's stuck:**
Nothing blocking right now. Confidence threshold (0.35) is a guess — will
tune once eval questions exist in Week 3.

**3 goals for next week (Week 3):**
1. Build the Compare Two Documents mini-extension.
2. Confirm the existing test suite passes and capture a screenshot for
   the submission.
3. Write ADR-002 and ADR-003, polish the README to the full Milestone 1
   standard (architecture diagram image, known limitations section, etc.).

**One thing I'd like help from my mentor on:**
Whether a 0.35 similarity threshold is reasonable for the out-of-domain
guardrail, or if there's a better default to start from before I have
eval data to tune against.

---

## Known Limitations (current stage)

- Scanned/image-only PDFs aren't supported (no OCR).
- The 0.35 guardrail threshold is unvalidated against real eval data yet.
- Only ADR-001 exists so far — ADR-002 and ADR-003 are drafted but held
  back until Week 3 per the deliverables schedule.

---

## License

MIT — see [LICENSE](LICENSE).
