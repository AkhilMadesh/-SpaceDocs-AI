"""
evaluation/ragas_metrics.py

PHASE 11 — Evaluation (RAGAS framework integration)

Purpose:
    Use the actual RAGAS library to compute standardized RAG quality metrics:
        - Faithfulness        : is the answer grounded in retrieved context?
        - Answer Relevancy    : does the answer address the question?
        - Context Precision   : are retrieved chunks relevant?
        - Context Recall      : did retrieval surface everything needed?

Note for beginners:
    RAGAS itself calls an LLM internally to JUDGE your RAG system's outputs.
    This means running this script consumes additional Gemini/OpenAI API calls
    beyond your normal app usage — that's expected and normal for evaluation.

Usage:
    python -m evaluation.ragas_metrics
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

from backend.llm.gemini_client import generate_answer
from backend.retrieval.retriever import retrieve

EVAL_QUESTIONS_PATH = Path(__file__).parent / "eval_questions.json"


def build_ragas_dataset() -> Dataset:
    """
    Build a HuggingFace Dataset in the structure RAGAS expects:
        question, answer, contexts (list of str), ground_truth
    """
    with open(EVAL_QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    records = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

    for item in questions:
        q = item["question"]
        rag_result = generate_answer(q)
        retrieved_chunks = retrieve(q)

        records["question"].append(q)
        records["answer"].append(rag_result["answer"])
        records["contexts"].append([c.text for c in retrieved_chunks])
        # Using the expected keywords joined as a rough proxy ground truth
        records["ground_truth"].append(" ".join(item["expected_answer_contains"]))

    return Dataset.from_dict(records)


def run_ragas_evaluation():
    dataset = build_ragas_dataset()

    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )

    print("=== RAGAS METRICS ===")
    print(results)
    return results


if __name__ == "__main__":
    run_ragas_evaluation()
