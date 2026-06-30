"""
app/main.py

Main Entry Point — Week 1-2 skinny build.

Run with:
    streamlit run app/main.py

Layout:
    Sidebar  -> Upload PDFs, view documents, delete documents
    Main     -> Question input, chat history, answers, citations

Note: Summarize / Quiz / Compare tabs exist in frontend/features.py but are
Week 3+ deliverables (mini-extension + later additions) per
02_Technical_Problem_Compendium.md. They're feature-flagged off here so the
Week 2 "skinny end-to-end" submission only shows what's actually been
built, tested, and documented at this stage. Flip SHOW_WEEK3_FEATURES to
True once those land.
"""

import sys
from pathlib import Path

import streamlit as st

# Ensure the project root is on sys.path so "backend." and "frontend." imports work
# regardless of which directory `streamlit run` is invoked from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frontend.chat import render_chat
from frontend.sidebar import render_sidebar

SHOW_WEEK3_FEATURES = False  # flip to True in Week 3 once the mini-extension lands

st.set_page_config(
    page_title="SpaceDocs AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Dark mode + modern styling ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
    }
    section[data-testid="stSidebar"] {
        background-color: #161B22;
    }
    h1, h2, h3 {
        color: #58A6FF;
    }
    .stChatMessage {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛰️ SpaceDocs AI")
st.caption("Explore NASA, ISRO, and Space Research documents through natural language.")
st.caption("Status: Week 2 — skinny end-to-end build · Problem statement I2")

docs = render_sidebar()
render_chat()

if SHOW_WEEK3_FEATURES:
    from frontend.features import render_features
    render_features(docs)
