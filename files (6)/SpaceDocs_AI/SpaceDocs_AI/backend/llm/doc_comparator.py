"""
backend/llm/doc_comparator.py

PHASE 12 — Mini Extension: Compare Two Documents

Purpose:
    Let users compare two uploaded documents (e.g. Chandrayaan-3 vs Artemis
    mission reports) and get a structured breakdown of similarities,
    differences, and unique aspects of each.

Approach:
    1. Retrieve a sample of chunks from EACH document independently.
    2. Pass both sets of excerpts to Gemini with a comparison-focused prompt.
    3. Return a structured answer covering objectives, technology, and outcomes.
"""

import os

import google.generativeai as genai
from dotenv import load_dotenv

from backend.vectordb.chroma_client import get_collection

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

COMPARISON_PROMPT = """You are comparing two space-research documents based ONLY on the \
excerpts provided below. Do not use outside knowledge.

DOCUMENT A ({filename_a}) EXCERPTS:
{context_a}

DOCUMENT B ({filename_b}) EXCERPTS:
{context_b}

USER QUESTION: {question}

Provide a clear, structured comparison covering relevant aspects such as objectives, \
technology/architecture, timeline, and outcomes — but only where the excerpts support it. \
If something cannot be determined from the excerpts, say so explicitly rather than guessing.
"""


def _get_document_chunks(document_id: str, max_chunks: int = 12) -> tuple[str, str]:
    """Fetch a sample of chunks and the filename for a given document_id."""
    collection = get_collection()
    results = collection.get(where={"document_id": document_id}, limit=max_chunks)

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    filename = metadatas[0]["filename"] if metadatas else "Unknown document"
    context = "\n\n".join(documents) if documents else "(no content found)"

    return filename, context


def compare_documents(document_id_a: str, document_id_b: str, question: str) -> str:
    """
    Compare two documents and answer a question about their relationship.

    Args:
        document_id_a: first document's ID.
        document_id_b: second document's ID.
        question: e.g. "What changed?", "How do these documents differ?"

    Returns:
        A grounded comparison answer as a string.
    """
    filename_a, context_a = _get_document_chunks(document_id_a)
    filename_b, context_b = _get_document_chunks(document_id_b)

    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
        return "(Set GOOGLE_API_KEY in .env to enable document comparison.)"

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name=LLM_MODEL)

    prompt = COMPARISON_PROMPT.format(
        filename_a=filename_a,
        context_a=context_a,
        filename_b=filename_b,
        context_b=context_b,
        question=question,
    )

    response = model.generate_content(prompt)
    return response.text.strip()
