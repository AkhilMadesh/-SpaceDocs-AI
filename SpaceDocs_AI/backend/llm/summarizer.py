"""
backend/llm/summarizer.py

Feature: Document Summaries

Purpose:
    Generate a concise summary of an uploaded document using Gemini,
    grounded in a sample of its actual chunks (not the whole document,
    to stay within prompt limits on large PDFs).
"""

import os

import google.generativeai as genai
from dotenv import load_dotenv

from backend.vectordb.chroma_client import get_collection

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

SUMMARY_PROMPT = """Summarize the following document excerpts in 4-6 sentences. \
Focus on the document's purpose, key topics, and any notable findings or specifications. \
Write for a student or researcher audience.

EXCERPTS:
{context}

SUMMARY:"""


def summarize_document(document_id: str, max_chunks: int = 12) -> str:
    """
    Generate a summary for a document by sampling its stored chunks.

    Args:
        document_id: the document to summarize.
        max_chunks: how many chunks to sample (keeps prompt size reasonable).

    Returns:
        A short natural-language summary string.
    """
    collection = get_collection()
    results = collection.get(where={"document_id": document_id}, limit=max_chunks)

    documents = results.get("documents", [])
    if not documents:
        return "No content available to summarize for this document."

    context = "\n\n".join(documents)

    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
        return "(Set GOOGLE_API_KEY in .env to enable AI-generated summaries.)"

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name=LLM_MODEL)

    prompt = SUMMARY_PROMPT.format(context=context)
    response = model.generate_content(prompt)
    return response.text.strip()
