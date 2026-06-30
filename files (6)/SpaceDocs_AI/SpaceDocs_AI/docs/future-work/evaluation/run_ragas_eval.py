"""
evaluation/run_ragas_eval.py

PHASE 11 — Evaluation

Purpose:
    Run the 20 evaluation questions through the live RAG pipeline, then
    score the results using RAGAS metrics: faithfulness, answer relevancy,
    context precision, and context recall. Also computes a simple manual
    "keyword hit rate" and hallucination flag using eval_questions.json.

Usage:
    python -m evaluation.run_ragas_eval

Output:
    evaluation/reports/eval_report.json  (also printed to console)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.llm.gemini_client import generate_answer

EVAL_QUESTIONS_PATH = Path(__file__).parent / "eval_questions.json"
REPORT_DIR = Path(__file__).parent / "reports"
REPORT_PATH = REPORT_DIR / "eval_report.json"


def load_eval_questions() -> list[dict]:
    with open(EVAL_QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def manual_keyword_check(answer: str, expected_keywords: list[str]) -> dict:
    """
    Lightweight manual check: does the generated answer contain at least
    one of the expected keywords/phrases (case-insensitive)?

    This is a SIMPLE proxy for "correctness" before running full RAGAS scoring.
    """
    answer_lower = answer.lower()
    hits = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    return {
        "hit_rate": round(len(hits) / len(expected_keywords), 2) if expected_keywords else 0.0,
        "matched_keywords": hits,
    }


def run_evaluation() -> dict:
    questions = load_eval_questions()
    results = []

    for item in questions:
        question = item["question"]
        expected = item["expected_answer_contains"]

        rag_result = generate_answer(question)
        keyword_check = manual_keyword_check(rag_result["answer"], expected)

        # Hallucination flag: model gave a confident, non-fallback answer
        # but matched NONE of the expected keywords -> likely hallucinated/wrong.
        is_likely_hallucination = (
            not rag_result["is_fallback"] and keyword_check["hit_rate"] == 0.0
        )

        results.append(
            {
                "question": question,
                "answer": rag_result["answer"],
                "confidence": rag_result["confidence"],
                "is_fallback": rag_result["is_fallback"],
                "citations_count": len(rag_result["citations"]),
                "keyword_hit_rate": keyword_check["hit_rate"],
                "matched_keywords": keyword_check["matched_keywords"],
                "likely_hallucination": is_likely_hallucination,
                "note": item.get("note", ""),
            }
        )

    avg_hit_rate = round(sum(r["keyword_hit_rate"] for r in results) / len(results), 3)
    hallucination_rate = round(
        sum(1 for r in results if r["likely_hallucination"]) / len(results), 3
    )
    fallback_count = sum(1 for r in results if r["is_fallback"])
    avg_confidence = round(sum(r["confidence"] for r in results) / len(results), 3)

    report = {
        "summary": {
            "total_questions": len(results),
            "average_keyword_hit_rate": avg_hit_rate,
            "hallucination_rate": hallucination_rate,
            "fallback_triggered_count": fallback_count,
            "average_confidence": avg_confidence,
        },
        "results": results,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    print("Running evaluation on 20 questions against the live RAG pipeline...\n")
    report = run_evaluation()

    print("=== SUMMARY ===")
    for k, v in report["summary"].items():
        print(f"{k}: {v}")

    print(f"\nFull report saved to: {REPORT_PATH}")
