"""
backend/llm/quiz_generator.py

Feature: Quiz Generation

Purpose:
    Generate multiple-choice quiz questions grounded in a document's content,
    useful for students/researchers self-testing their understanding.
"""

import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

from backend.vectordb.chroma_client import get_collection

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

QUIZ_PROMPT = """Based ONLY on the excerpts below, generate {num_questions} multiple-choice \
quiz questions to test understanding of this material. Each question must have exactly \
4 options with only one correct answer.

Respond ONLY with valid JSON in this exact format, no extra text:
[
  {{
    "question": "...",
    "options": ["A...", "B...", "C...", "D..."],
    "correct_answer": "A...",
    "explanation": "..."
  }}
]

EXCERPTS:
{context}
"""


def generate_quiz(document_id: str, num_questions: int = 5, max_chunks: int = 15) -> list[dict]:
    """
    Generate a quiz grounded in a document's stored chunks.

    Returns:
        List of question dicts: {question, options, correct_answer, explanation}
    """
    collection = get_collection()
    results = collection.get(where={"document_id": document_id}, limit=max_chunks)
    documents = results.get("documents", [])

    if not documents:
        return []

    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
        return [{"question": "Set GOOGLE_API_KEY in .env to enable quiz generation.",
                  "options": ["OK"], "correct_answer": "OK", "explanation": ""}]

    context = "\n\n".join(documents)
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name=LLM_MODEL)

    prompt = QUIZ_PROMPT.format(num_questions=num_questions, context=context)
    response = model.generate_content(prompt)

    raw_text = response.text.strip()
    # Strip markdown code fences if Gemini wraps the JSON in ```json ... ```
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        quiz = json.loads(raw_text)
    except json.JSONDecodeError:
        quiz = [{"question": "Quiz generation failed to parse — try again.",
                  "options": ["OK"], "correct_answer": "OK", "explanation": raw_text[:200]}]

    return quiz
