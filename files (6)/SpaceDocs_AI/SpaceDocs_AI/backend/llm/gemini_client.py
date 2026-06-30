"""
backend/llm/gemini_client.py

PHASE 9 — Gemini Integration

Purpose:
    Send the user's question + retrieved chunks to Gemini 2.5 Flash, and force
    the model to answer ONLY using the provided context — never from its own
    general knowledge. This is what makes answers trustworthy and citeable.

Guardrails implemented:
    1. Strict grounding instruction in the system prompt.
    2. Explicit fallback phrase when context is insufficient:
           "I don't know based on uploaded documents."
    3. Out-of-domain detection — if retrieved chunks have low similarity
       scores, we treat the query as out-of-domain BEFORE even calling the LLM.

Why guardrails matter:
    Without them, an LLM will happily "hallucinate" a plausible-sounding
    answer about Chandrayaan-3 even if you uploaded a manual about CubeSats.
    Grounding + guardrails are what separate a real RAG system from "an LLM
    with extra steps."
"""

import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

from backend.retrieval.retriever import RetrievedChunk, retrieve

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# Below this similarity score, we consider retrieval too weak to trust —
# this is the out-of-domain guardrail's main trigger.
MIN_CONFIDENCE_THRESHOLD = 0.35

FALLBACK_RESPONSE = "I don't know based on uploaded documents."

SYSTEM_PROMPT = """You are SpaceDocs AI, an assistant that answers questions \
strictly using the CONTEXT provided below, extracted from user-uploaded \
space-research documents (NASA, ISRO, mission reports, engineering manuals).

RULES (follow exactly):
1. Use ONLY the information in the CONTEXT to answer. Do not use outside knowledge.
2. If the CONTEXT does not contain enough information to answer confidently, \
respond with EXACTLY this sentence and nothing else: "I don't know based on uploaded documents."
3. Do not make up sources, page numbers, or facts not present in the CONTEXT.
4. Keep answers clear, concise, and technically accurate.
5. Where relevant, mention which document/page the information came from.
"""


def _get_client() -> genai.Client:
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Add it to your .env file. "
            "Get a free key at https://aistudio.google.com/app/apikey"
        )
    return genai.Client(api_key=GOOGLE_API_KEY)


def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a labeled context block for the prompt."""
    blocks = []
    for i, c in enumerate(chunks, start=1):
        blocks.append(
            f"[Context {i} | Source: {c.filename} | Page: {c.page_number}]\n{c.text}"
        )
    return "\n\n".join(blocks)


def is_out_of_domain(chunks: list[RetrievedChunk]) -> bool:
    """
    Guardrail check: if the BEST retrieved chunk still has a low similarity
    score, the question is likely unrelated to the uploaded documents.
    """
    if not chunks:
        return True
    best_score = max(c.similarity_score for c in chunks)
    return best_score < MIN_CONFIDENCE_THRESHOLD


def generate_answer(query: str, document_filter: str | None = None) -> dict:
    """
    Full RAG answer generation: retrieve -> guardrail check -> generate -> cite.

    Args:
        query: the user's question.
        document_filter: optional document_id to scope retrieval to one document.

    Returns:
        dict with keys: answer, citations (list), confidence (float), is_fallback (bool)
    """
    chunks = retrieve(query, document_filter=document_filter)

    # --- Guardrail: out-of-domain / no relevant context found ---
    if is_out_of_domain(chunks):
        return {
            "answer": FALLBACK_RESPONSE,
            "citations": [],
            "confidence": 0.0,
            "is_fallback": True,
        }

    client = _get_client()
    context_block = _build_context_block(chunks)
    prompt = f"CONTEXT:\n{context_block}\n\nQUESTION:\n{query}"

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    answer_text = response.text.strip()

    # If the model itself decided it doesn't know, respect that.
    is_fallback = FALLBACK_RESPONSE.lower() in answer_text.lower()

    avg_confidence = round(sum(c.similarity_score for c in chunks) / len(chunks), 4)

    return {
        "answer": answer_text,
        "citations": [
            {"source": c.filename, "page": c.page_number, "confidence": c.similarity_score}
            for c in chunks
        ],
        "confidence": avg_confidence,
        "is_fallback": is_fallback,
    }


if __name__ == "__main__":
    # Quick manual test — run with: python -m backend.llm.gemini_client "your question"
    import sys

    if len(sys.argv) < 2:
        print('Usage: python -m backend.llm.gemini_client "your question here"')
        sys.exit(1)

    result = generate_answer(sys.argv[1])
    print("ANSWER:\n", result["answer"])
    print("\nCITATIONS:")
    for c in result["citations"]:
        print(f"  Source: {c['source']} | Page: {c['page']} | Confidence: {c['confidence']}")
    print(f"\nOverall confidence: {result['confidence']}")
