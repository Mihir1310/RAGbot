"""Streamlit chat UI over the RAG pipeline.

Week 1, Days 5-7. Run with: `uv run streamlit run src/ragbot/app.py`
"""

from ragbot.app import sources_list
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
        sources_list = []

        def token_generator():
            nonlocal sources_list
            for token, chunks in ask_stream(question):
                if not sources_list:
                    sources_list = chunks
                yield token

        full_answer = st.write_stream(token_generator())

        if sources_list:
            with st.expander("Sources used"):
                for i, chunk in enumerate(sources_list, 1):
                    st.markdown(f"**Chunk {i}**")
                    st.caption(chunk)

    st.session_state.history.append(("assistant", full_answer))
