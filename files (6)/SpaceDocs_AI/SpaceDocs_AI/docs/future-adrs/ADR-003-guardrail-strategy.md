# ADR-003: Out-of-Domain & Hallucination Guardrail Strategy

**Status:** Accepted
**Date:** 2026-06-27

## Context

A core requirement is that SpaceDocs AI must NOT hallucinate answers about
topics outside the uploaded documents, and must clearly say
**"I don't know based on uploaded documents."** when it lacks grounding.
We needed a strategy that catches out-of-domain queries reliably without
adding significant latency or cost.

## Decision

We implemented a **two-layer guardrail**:

1. **Pre-generation similarity threshold check** (`is_out_of_domain()` in
   `backend/llm/gemini_client.py`): if the best-matching retrieved chunk has
   a cosine similarity score below `0.35`, we skip the LLM call entirely and
   return the fallback message directly.
2. **Prompt-level instruction guardrail**: the system prompt explicitly
   instructs Gemini to answer ONLY from the provided context and to return
   the exact fallback sentence if the context is insufficient — even when
   retrieval *did* return chunks above the threshold but they don't actually
   answer the specific question asked.

## Rationale

- Relying on the LLM alone (layer 2) is necessary but not sufficient — LLMs
  can still occasionally generate a plausible-sounding answer from weakly
  related context.
- Relying on the similarity threshold alone (layer 1) is also insufficient —
  some valid in-domain questions can have moderate-but-legitimate similarity
  scores, and being too aggressive would cause false "I don't know" answers.
- Combining both layers: the threshold catches CLEARLY out-of-domain queries
  cheaply (no LLM call needed, saving cost/latency), while the prompt
  instruction catches subtler cases where retrieval succeeded but content
  relevance did not.

## Consequences

- **Positive:** Significantly reduces hallucination rate (see Phase 11
  evaluation report `hallucination_rate` metric); saves API calls on clearly
  irrelevant queries.
- **Negative:** The `0.35` threshold is a heuristic tuned manually, not
  learned — it may need adjustment based on which embedding model is used,
  since different models produce different similarity score distributions.
- **Mitigation:** The threshold is a module-level constant
  (`MIN_CONFIDENCE_THRESHOLD`) that can be tuned by analyzing the
  `evaluation/reports/eval_report.json` output (specifically, comparing
  confidence scores for true in-domain vs. true out-of-domain test
  questions) without touching any other logic.
