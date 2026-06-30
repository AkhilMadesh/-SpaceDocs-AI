# Future ADRs (Drafted, Not Yet Due)

These ADRs were drafted ahead of schedule but are **Week 3 deliverables**
per `03_Deliverables_Specification.md` ("2 more ADRs" land in Week 3,
bringing the total to 3). They live here so the Week 2 submission only
surfaces ADR-001 — the one that's actually due.

- `ADR-002-embedding-model-choice.md` — will move to `docs/adr/` in Week 3
- `ADR-003-guardrail-strategy.md` — will move to `docs/adr/` in Week 3

## Known gap to fix before Week 3
`backend/llm/summarizer.py`, `quiz_generator.py`, and `doc_comparator.py`
still import the deprecated `google.generativeai` SDK (same issue that was
already fixed in `gemini_client.py` for the core Q&A path). They aren't
wired into the Week 2 app, so this isn't blocking the skinny demo — but it
needs fixing before the Week 3 mini-extension (Compare Two Documents)
ships, since `doc_comparator.py` is exactly what that feature depends on.
