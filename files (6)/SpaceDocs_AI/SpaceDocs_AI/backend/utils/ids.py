"""
backend/utils/ids.py

Small utility to generate a stable, unique document_id from a file's content.
Using a content hash (not just the filename) means re-uploading the exact
same PDF twice doesn't create duplicate entries in the vector store.
"""

import hashlib


def generate_document_id(filepath: str) -> str:
    """Generate a short, stable hash-based ID from file contents."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()[:16]
