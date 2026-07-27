"""Streamlit chat UI over the RAG pipeline.

Week 1, Days 5-7. Run with: `uv run streamlit run src/ragbot/app.py`
"""

import streamlit as st

from ragbot.rag import ask

st.set_page_config(page_title="RAGbot", page_icon="")
st.title("RAGbot — Local Document Assistant")

if "history" not in st.session_state:
    st.session_state.history = []

for role, content in st.session_state.history:
    with st.chat_message(role):
        st.write(content)

question = st.chat_input("Ask something about your documents...")
if question:
    st.session_state.history.append(("user", question))
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"), st.spinner("Thinking..."):
        answer, sources = ask(question)
        st.write(answer)
        if sources:
            with st.expander("Sources used"):
                for i, chunk in enumerate(sources, 1):
                    st.markdown(f"**Chunk {i}**")
                    st.caption(chunk)

    st.session_state.history.append(("assistant", answer))
