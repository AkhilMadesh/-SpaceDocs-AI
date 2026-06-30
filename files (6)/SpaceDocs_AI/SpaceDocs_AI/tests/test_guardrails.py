"""
tests/test_guardrails.py

Run with: pytest tests/test_guardrails.py -v

Tests the out-of-domain guardrail logic WITHOUT calling the live Gemini API
(no API key required to run these).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.llm.gemini_client import is_out_of_domain
from backend.retrieval.retriever import RetrievedChunk


def make_chunk(score: float) -> RetrievedChunk:
    return RetrievedChunk(
        text="sample text",
        filename="sample.pdf",
        page_number=1,
        chunk_index=0,
        similarity_score=score,
    )


def test_empty_chunks_is_out_of_domain():
    assert is_out_of_domain([]) is True


def test_low_similarity_is_out_of_domain():
    chunks = [make_chunk(0.10), make_chunk(0.20)]
    assert is_out_of_domain(chunks) is True


def test_high_similarity_is_in_domain():
    chunks = [make_chunk(0.85), make_chunk(0.60)]
    assert is_out_of_domain(chunks) is False


def test_threshold_boundary():
    # Just above the 0.35 threshold should be considered in-domain
    chunks = [make_chunk(0.36)]
    assert is_out_of_domain(chunks) is False

    # Just below should be out-of-domain
    chunks = [make_chunk(0.34)]
    assert is_out_of_domain(chunks) is True
