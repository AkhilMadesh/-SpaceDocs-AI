"""
backend/ingestion/pdf_loader.py

PHASE 4 — PDF Parsing

Purpose:
    Extract clean, readable text from PDFs using PyMuPDF (imported as "fitz").
    Handles multi-page documents, strips garbage characters, and normalizes
    whitespace so downstream chunking/embedding works on clean text.

Why PyMuPDF over other libraries (e.g. PyPDF2)?
    - Much faster on large technical PDFs (NASA/ISRO reports can be 100+ pages).
    - Better at preserving reading order in multi-column layouts.
    - Gives per-page access, which we need for accurate page-level citations.
"""

import re
from dataclasses import dataclass, field

import fitz  # PyMuPDF


@dataclass
class PageContent:
    """Holds the extracted text for a single PDF page."""
    page_number: int  # 1-indexed, human-friendly page numbers
    text: str


@dataclass
class ParsedDocument:
    """Holds the full result of parsing one PDF."""
    filename: str
    num_pages: int
    pages: list[PageContent] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Concatenate all pages into one string (used for whole-doc summaries)."""
        return "\n\n".join(p.text for p in self.pages)


def _clean_text(raw_text: str) -> str:
    """
    Normalize messy PDF text extraction artifacts.

    PDFs often produce:
      - Multiple consecutive spaces/newlines
      - Stray control characters
      - Hyphenated line breaks (e.g. "satel-\nlite" -> "satellite")
    """
    # Fix hyphenated line breaks
    text = re.sub(r"-\n(?=[a-z])", "", raw_text)

    # Collapse multiple newlines into a single paragraph break
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Collapse multiple spaces/tabs
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


def parse_pdf(filepath: str) -> ParsedDocument:
    """
    Parse a PDF file and return structured, cleaned text per page.

    Args:
        filepath: path to the PDF file on disk.

    Returns:
        ParsedDocument containing per-page text and metadata.

    Raises:
        ValueError: if the file cannot be opened or contains no extractable text.
    """
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        raise ValueError(f"Could not open PDF '{filepath}': {e}") from e

    pages: list[PageContent] = []

    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            raw_text = page.get_text("text")
            cleaned = _clean_text(raw_text)

            # Skip entirely blank pages (common in scanned/cover pages)
            if cleaned:
                pages.append(PageContent(page_number=page_index + 1, text=cleaned))
    finally:
        doc.close()

    if not pages:
        raise ValueError(
            f"No extractable text found in '{filepath}'. "
            "This may be a scanned/image-only PDF that requires OCR."
        )

    filename = filepath.split("/")[-1]
    return ParsedDocument(filename=filename, num_pages=len(pages), pages=pages)


if __name__ == "__main__":
    # Quick manual test — run with: python -m backend.ingestion.pdf_loader <path>
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m backend.ingestion.pdf_loader <path_to_pdf>")
        sys.exit(1)

    result = parse_pdf(sys.argv[1])
    print(f"Parsed '{result.filename}' — {result.num_pages} pages with text")
    print("--- Preview of page 1 ---")
    print(result.pages[0].text[:500])
