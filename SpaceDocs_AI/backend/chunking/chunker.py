"""
backend/chunking/chunker.py

PHASE 5 — Chunking

Purpose:
    Split parsed PDF text into smaller, overlapping "chunks" that are small
    enough to embed meaningfully and large enough to retain context.

Why chunking is needed:
    - Embedding models have token limits and lose accuracy on very long text.
    - LLMs can only fit a limited amount of context in a prompt.
    - Smaller chunks let retrieval be PRECISE — you get back the 2 paragraphs
      that actually answer the question, not an entire 40-page PDF.

Chunk strategy used here: RecursiveCharacterTextSplitter (via LangChain)
    - Tries to split on paragraph breaks first, then sentences, then words.
    - This respects natural language boundaries instead of cutting mid-sentence.

Tradeoffs:
    - Smaller chunks  -> more precise retrieval, but less surrounding context.
    - Larger chunks   -> more context per chunk, but retrieval gets "noisier"
                         (irrelevant text riding along with the relevant part).
    - Overlap         -> prevents losing meaning at chunk boundaries, but
                         increases total storage and embedding cost slightly.

Defaults used (good for technical/aerospace documents):
    CHUNK_SIZE    = 500 characters
    CHUNK_OVERLAP = 100 characters
"""

import os
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.ingestion.pdf_loader import ParsedDocument

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))


@dataclass
class Chunk:
    """A single chunk of text with traceable metadata for citations."""
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    chunk_index: int
    text: str


def get_splitter() -> RecursiveCharacterTextSplitter:
    """
    Build the text splitter.

    separators are tried IN ORDER:
      1. "\n\n" — paragraph breaks (best split point)
      2. "\n"   — line breaks
      3. ". "   — sentence ends
      4. " "    — word boundaries (last resort)
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def chunk_document(parsed_doc: ParsedDocument, document_id: str) -> list[Chunk]:
    """
    Convert a ParsedDocument into a list of Chunks, preserving page-level
    traceability (needed for accurate citations in Phase 9).

    Args:
        parsed_doc: output of pdf_loader.parse_pdf()
        document_id: a stable unique ID for this document (e.g. a hash or UUID)

    Returns:
        List of Chunk objects ready for embedding.
    """
    splitter = get_splitter()
    chunks: list[Chunk] = []
    global_index = 0

    for page in parsed_doc.pages:
        page_splits = splitter.split_text(page.text)

        for split_text in page_splits:
            chunk = Chunk(
                chunk_id=f"{document_id}_p{page.page_number}_c{global_index}",
                document_id=document_id,
                filename=parsed_doc.filename,
                page_number=page.page_number,
                chunk_index=global_index,
                text=split_text,
            )
            chunks.append(chunk)
            global_index += 1

    return chunks


if __name__ == "__main__":
    # Quick manual test — run with: python -m backend.chunking.chunker <path_to_pdf>
    import sys

    from backend.ingestion.pdf_loader import parse_pdf

    if len(sys.argv) < 2:
        print("Usage: python -m backend.chunking.chunker <path_to_pdf>")
        sys.exit(1)

    parsed = parse_pdf(sys.argv[1])
    doc_chunks = chunk_document(parsed, document_id="test_doc_001")

    print(f"Created {len(doc_chunks)} chunks from {parsed.num_pages} pages\n")
    for c in doc_chunks[:3]:
        print(f"[{c.chunk_id}] (page {c.page_number}) -> {c.text[:120]}...\n")
