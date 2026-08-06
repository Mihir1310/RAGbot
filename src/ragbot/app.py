"""Streamlit chat UI over the RAG pipeline.

Week 1, Days 5-7. Run with: `uv run streamlit run src/ragbot/app.py`
"""

import streamlit as st

from ragbot.rag import ask_stream

st.set_page_config(page_title="RAGbot", page_icon="🤖")
st.title("RAGbot — Financial & Document Assistant")

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

    with st.chat_message("assistant"):
        sources_holder = []

        def token_generator():
            for token, chunks in ask_stream(question):
                if not sources_holder:
                    sources_holder.extend(chunks)
                yield token

        full_answer = st.write_stream(token_generator())

        if sources_holder:
            with st.expander("Sources used"):
                for i, chunk in enumerate(sources_holder, 1):
                    st.markdown(f"**Chunk {i}**")
                    st.caption(chunk)

    st.session_state.history.append(("assistant", full_answer))
