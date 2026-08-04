import streamlit as st
from langchain_community.llms import Ollama
from rag_pipeline import get_retriever

# Setup Page
st.set_page_config(page_title="SEC 10-K Analyzer", page_icon="📈")
st.title("📈 SEC 10-K Financial Analyzer")
st.write("Ask questions about the uploaded SEC 10-K document.")

# Initialize RAG and Model (caching prevents reloading on every UI interaction)
@st.cache_resource
def load_rag_components():
    retriever = get_retriever()
    # Assuming user runs phi3 locally via Ollama
    llm = Ollama(model="phi3")
    return retriever, llm

retriever, llm = load_rag_components()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("E.g., What are the primary risk factors?"):
    # Add User Message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing document..."):
            # 1. Retrieve relevant documents
            docs = retriever.invoke(prompt)
            context = "\n\n".join([doc.page_content for doc in docs])

            # 2. Build prompt for the LLM
            system_prompt = f"""You are a helpful financial analyst. Use the following context extracted from an SEC 10-K report to answer the user's question.
            If you don't know the answer based on the context, say so.

            Context: {context}

            Question: {prompt}

            Answer:"""

            # 3. Call local Ollama model
            try:
                response = llm.invoke(system_prompt)
            except Exception as e:
                response = f"⚠️ Error connecting to Ollama: {e}\n\nPlease ensure you have installed Ollama and run `ollama run phi3` in your terminal."

            st.markdown(response)

    # Add Assistant Message to History
    st.session_state.messages.append({"role": "assistant", "content": response})
