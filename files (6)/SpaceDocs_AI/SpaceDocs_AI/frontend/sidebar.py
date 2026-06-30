"""
frontend/sidebar.py

PHASE 10 — Streamlit Interface (Sidebar)

Purpose:
    Renders the sidebar: PDF upload, list of uploaded documents with
    metadata, and delete buttons.
"""

import streamlit as st

from backend.ingestion.metadata_store import delete_upload, list_uploads
from backend.ingestion.pipeline import ingest_pdf
from backend.utils.ids import generate_document_id
from backend.vectordb.chroma_client import delete_document


def render_sidebar():
    """Render the full sidebar UI. Returns the list of current uploads."""
    st.sidebar.title("🛰️ SpaceDocs AI")
    st.sidebar.caption("NASA · ISRO · Space Research Q&A")

    st.sidebar.divider()
    st.sidebar.subheader("📤 Upload Documents")

    uploaded_files = st.sidebar.file_uploader(
        "Upload PDFs (NASA/ISRO reports, manuals, papers)",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            already_processed = uploaded_file.name in st.session_state.get("processed_files", set())
            if not already_processed:
                with st.sidebar.status(f"Processing {uploaded_file.name}..."):
                    summary = ingest_pdf(uploaded_file.getvalue(), uploaded_file.name)
                    st.write(f"✅ {summary['chunks_created']} chunks created from {summary['pages']} pages")

                st.session_state.setdefault("processed_files", set()).add(uploaded_file.name)
                st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("📚 Your Documents")

    docs = list_uploads()

    if not docs:
        st.sidebar.info("No documents uploaded yet.")
    else:
        for doc in docs:
            with st.sidebar.expander(f"📄 {doc['filename']}"):
                st.write(f"**Pages:** {doc['pages']}")
                st.write(f"**Size:** {doc['size_mb']} MB")
                st.write(f"**Uploaded:** {doc['uploaded_at']}")

                if st.button("🗑️ Delete", key=f"delete_{doc['filename']}"):
                    document_id = generate_document_id(doc["filepath"])
                    delete_document(document_id)
                    delete_upload(doc["filename"])
                    st.session_state.get("processed_files", set()).discard(doc["filename"])
                    st.rerun()

    return docs
