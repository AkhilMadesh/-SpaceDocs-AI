"""
backend/ingestion/metadata_store.py

PHASE 3 — PDF Upload System

Purpose:
    When a user uploads a PDF, we don't just save the file — we also track
    metadata about it (filename, page count, size, upload time). This metadata
    is shown in the Streamlit sidebar and used later for citations.

Why a separate file for this?
    Keeping "bookkeeping" (metadata) separate from "parsing" (pdf_loader.py)
    follows the single-responsibility principle: each file does ONE job.
"""

import json
import os
from datetime import datetime
from pathlib import Path

METADATA_FILE = Path("data/uploads/_metadata.json")


def _load_metadata() -> dict:
    """Load existing metadata JSON, or return an empty dict if none exists yet."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_metadata(metadata: dict) -> None:
    """Persist metadata dict back to disk as JSON."""
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def register_upload(filename: str, filepath: str, num_pages: int) -> dict:
    """
    Record a newly uploaded PDF's metadata.

    Args:
        filename: original filename, e.g. "chandrayaan3_report.pdf"
        filepath: where it was saved on disk
        num_pages: total page count (computed during parsing)

    Returns:
        The metadata entry that was just created.
    """
    metadata = _load_metadata()

    file_size_bytes = os.path.getsize(filepath)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    entry = {
        "filename": filename,
        "filepath": filepath,
        "pages": num_pages,
        "size_mb": file_size_mb,
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
    }

    metadata[filename] = entry
    _save_metadata(metadata)
    return entry


def list_uploads() -> list[dict]:
    """Return metadata for every uploaded document (for the sidebar)."""
    metadata = _load_metadata()
    return list(metadata.values())


def delete_upload(filename: str) -> bool:
    """
    Remove a document's metadata entry and delete its file from disk.

    Returns:
        True if deletion succeeded, False if the file wasn't found.
    """
    metadata = _load_metadata()
    entry = metadata.pop(filename, None)

    if entry is None:
        return False

    filepath = Path(entry["filepath"])
    if filepath.exists():
        filepath.unlink()

    _save_metadata(metadata)
    return True
