#!/usr/bin/env python3
"""
to-eat-asu — Streamlit query interface (Milestone 5).

Run:
    streamlit run app.py        # then open http://localhost:8501

Streamlit (not Gradio) because gradio>=6.9 requires huggingface-hub>=1.2, which
conflicts with the huggingface-hub<1.0 that sentence-transformers 3.4.1 needs.
Streamlit has no huggingface-hub dependency, so the dependency tree stays clean.
"""

import streamlit as st

from rag import ask

st.set_page_config(page_title="to-eat-asu", page_icon="🍽️")

st.title("🍽️🍴😋 to-eat-asu")
st.caption(
    "Ask what ASU Tempe students actually say about food & dining — "
    "answers come only from real Reddit comments and Google reviews."
)

with st.form("ask_form"):
    question = st.text_input(
        "Your question",
        placeholder="e.g. Where can I get coffee on campus?",
    )
    submitted = st.form_submit_button("Ask")

if submitted:
    if not question.strip():
        st.warning("Type a food or dining question about ASU Tempe.")
    else:
        with st.spinner("Searching student reviews…"):
            result = ask(question)
        st.subheader("Answer")
        st.write(result["answer"])
        st.subheader("Retrieved from")
        if result["sources"]:
            for s in result["sources"]:
                st.markdown(f"- {s}")
        else:
            st.markdown("_No close matches — this is outside the student data we have._")

st.divider()
st.caption(
    "Try: “best meal plan for a freshman” · “vegetarian options at ASU” · "
    "“what do students think of Hassayampa?”"
)
