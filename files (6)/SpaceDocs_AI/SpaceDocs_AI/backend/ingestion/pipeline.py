"""
backend/ingestion/pipeline.py

Ties together Phases 3-7 into one function: upload -> parse -> chunk ->
embed -> store. This is what the Streamlit sidebar calls when a user
uploads a PDF.
"""

from pathlib import Path

from backend.chunking.chunker import chunk_document
from backend.ingestion.metadata_store import register_upload
from backend.ingestion.pdf_loader import parse_pdf
from backend.utils.ids import generate_document_id
from backend.vectordb.chroma_client import add_chunks

UPLOAD_DIR = Path("data/uploads")


def ingest_pdf(uploaded_file_bytes: bytes, original_filename: str) -> dict:
    """
    Full ingestion pipeline for one uploaded PDF.

    Args:
        uploaded_file_bytes: raw bytes from Streamlit's file_uploader.
        original_filename: the name of the file as uploaded by the user.

    Returns:
        dict summary: filename, document_id, pages, chunks_created.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / original_filename

    # Phase 3: save file to disk
    with open(save_path, "wb") as f:
        f.write(uploaded_file_bytes)

    # Phase 4: parse
    parsed = parse_pdf(str(save_path))

    # Generate a stable ID based on file content (prevents duplicate ingestion)
    document_id = generate_document_id(str(save_path))

    # Phase 3 (continued): register metadata
    register_upload(filename=original_filename, filepath=str(save_path), num_pages=parsed.num_pages)

    # Phase 5: chunk
    chunks = chunk_document(parsed, document_id=document_id)

    # Phase 6 + 7: embed and store in ChromaDB (embedding happens inside add_chunks)
    num_added = add_chunks(chunks)

    return {
        "filename": original_filename,
        "document_id": document_id,
        "pages": parsed.num_pages,
        "chunks_created": num_added,
    }
