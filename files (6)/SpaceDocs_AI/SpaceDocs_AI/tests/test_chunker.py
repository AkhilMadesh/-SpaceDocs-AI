"""
tests/test_chunker.py

Run with: pytest tests/test_chunker.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.chunking.chunker import chunk_document
from backend.ingestion.pdf_loader import PageContent, ParsedDocument


def test_chunk_document_basic():
    """Chunking should produce at least one chunk for non-trivial text."""
    long_text = "Space exploration is fascinating. " * 50
    parsed = ParsedDocument(
        filename="test.pdf",
        num_pages=1,
        pages=[PageContent(page_number=1, text=long_text)],
    )

    chunks = chunk_document(parsed, document_id="doc_test_001")

    assert len(chunks) > 0
    assert all(c.document_id == "doc_test_001" for c in chunks)
    assert all(c.filename == "test.pdf" for c in chunks)


def test_chunk_preserves_page_numbers():
    """Each chunk must remember which page it came from, for citations."""
    parsed = ParsedDocument(
        filename="multi_page.pdf",
        num_pages=2,
        pages=[
            PageContent(page_number=1, text="Page one content. " * 30),
            PageContent(page_number=2, text="Page two content. " * 30),
        ],
    )

    chunks = chunk_document(parsed, document_id="doc_test_002")

    page_1_chunks = [c for c in chunks if c.page_number == 1]
    page_2_chunks = [c for c in chunks if c.page_number == 2]

    assert len(page_1_chunks) > 0
    assert len(page_2_chunks) > 0


def test_chunk_ids_are_unique():
    """Every chunk must have a globally unique chunk_id."""
    parsed = ParsedDocument(
        filename="test.pdf",
        num_pages=1,
        pages=[PageContent(page_number=1, text="Some repeated text. " * 100)],
    )

    chunks = chunk_document(parsed, document_id="doc_test_003")
    chunk_ids = [c.chunk_id for c in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))
