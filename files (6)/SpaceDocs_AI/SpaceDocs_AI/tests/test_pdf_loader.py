"""
tests/test_pdf_loader.py

Run with: pytest tests/test_pdf_loader.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ingestion.pdf_loader import _clean_text


def test_clean_text_removes_hyphenated_linebreaks():
    raw = "The satel-\nlite launched successfully."
    cleaned = _clean_text(raw)
    assert "satellite" in cleaned
    assert "satel-" not in cleaned


def test_clean_text_collapses_multiple_spaces():
    raw = "This   has    too many     spaces."
    cleaned = _clean_text(raw)
    assert "  " not in cleaned


def test_clean_text_collapses_excess_newlines():
    raw = "Paragraph one.\n\n\n\n\nParagraph two."
    cleaned = _clean_text(raw)
    assert "\n\n\n" not in cleaned


def test_clean_text_strips_whitespace():
    raw = "   leading and trailing whitespace   "
    cleaned = _clean_text(raw)
    assert cleaned == cleaned.strip()
