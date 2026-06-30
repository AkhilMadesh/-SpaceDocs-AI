"""
frontend/features.py

PHASE 10/11/12 — Streamlit Interface (Extra Feature Tabs)

Purpose:
    Renders the Document Summaries, Quiz Generator, and Document Comparison
    tools as a tabbed section beneath the main chat area.
"""

import streamlit as st

from backend.llm.doc_comparator import compare_documents
from backend.llm.quiz_generator import generate_quiz
from backend.llm.summarizer import summarize_document
from backend.utils.ids import generate_document_id


def render_features(docs: list[dict]):
    """Render Summary / Quiz / Compare tabs. `docs` comes from list_uploads()."""
    if not docs:
        return

    st.divider()
    tab_summary, tab_quiz, tab_compare = st.tabs(["📝 Summarize", "🧠 Quiz Me", "🔁 Compare Documents"])

    doc_options = {d["filename"]: generate_document_id(d["filepath"]) for d in docs}

    with tab_summary:
        selected = st.selectbox("Choose a document to summarize", list(doc_options.keys()), key="summary_select")
        if st.button("Generate Summary"):
            with st.spinner("Summarizing..."):
                summary = summarize_document(doc_options[selected])
                st.info(summary)

    with tab_quiz:
        selected = st.selectbox("Choose a document to quiz on", list(doc_options.keys()), key="quiz_select")
        num_q = st.slider("Number of questions", 3, 10, 5)

        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz questions..."):
                quiz = generate_quiz(doc_options[selected], num_questions=num_q)
                st.session_state["current_quiz"] = quiz

        if "current_quiz" in st.session_state:
            for i, q in enumerate(st.session_state["current_quiz"], start=1):
                st.write(f"**Q{i}. {q['question']}**")
                answer = st.radio("Choose:", q["options"], key=f"quiz_q_{i}", label_visibility="collapsed")
                if st.button("Check", key=f"check_{i}"):
                    if answer == q["correct_answer"]:
                        st.success(f"Correct! {q.get('explanation', '')}")
                    else:
                        st.error(f"Not quite. Correct answer: {q['correct_answer']}. {q.get('explanation', '')}")

    with tab_compare:
        if len(doc_options) < 2:
            st.warning("Upload at least two documents to use the comparison feature.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                doc_a = st.selectbox("Document A", list(doc_options.keys()), key="compare_a")
            with col2:
                doc_b = st.selectbox(
                    "Document B",
                    [d for d in doc_options.keys() if d != doc_a],
                    key="compare_b",
                )

            compare_question = st.text_input(
                "What do you want to know?",
                value="How do these documents differ?",
            )

            if st.button("Compare"):
                with st.spinner("Comparing documents..."):
                    result = compare_documents(
                        doc_options[doc_a], doc_options[doc_b], compare_question
                    )
                    st.write(result)
