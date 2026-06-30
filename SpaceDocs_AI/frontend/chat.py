"""
frontend/chat.py

PHASE 10 — Streamlit Interface (Chat / Q&A Main Area)

Purpose:
    Renders the question input, conversation history, answers, and citations.
"""

import streamlit as st

from backend.llm.gemini_client import generate_answer


def render_chat():
    """Render the main chat Q&A interface with persistent conversation history."""
    st.subheader("💬 Ask a Question")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render existing conversation history
    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])
            if turn["citations"]:
                with st.expander("📌 Sources & Confidence"):
                    for c in turn["citations"]:
                        st.write(f"**{c['source']}** — Page {c['page']} — Confidence: `{c['confidence']}`")
            st.caption(f"Overall confidence: {turn['confidence']}")

    # New question input
    question = st.chat_input("Ask about Chandrayaan-3, PSLV, Artemis, CubeSats...")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                result = generate_answer(question)
                st.write(result["answer"])

                if result["citations"]:
                    with st.expander("📌 Sources & Confidence"):
                        for c in result["citations"]:
                            st.write(f"**{c['source']}** — Page {c['page']} — Confidence: `{c['confidence']}`")

                st.caption(f"Overall confidence: {result['confidence']}")

        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": result["answer"],
                "citations": result["citations"],
                "confidence": result["confidence"],
            }
        )
