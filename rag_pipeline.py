import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from create_pdf import create_sample_pdf

DATA_DIR = "data"
DB_DIR = "chroma_db"

def initialize_vector_db():
    # 0. Ensure the sample PDF exists
    pdf_path = create_sample_pdf()

    # 1. Load Document
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    # 3. Create Embeddings (using a small, CPU-friendly model)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Store in Vector Database
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    return vectorstore

def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    if not os.path.exists(DB_DIR):
        print("Vector DB not found. Initializing...")
        vectorstore = initialize_vector_db()
    else:
        vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

    return vectorstore.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    print("Testing RAG pipeline setup...")
    retriever = get_retriever()
    docs = retriever.invoke("What are the risk factors?")
    print(f"Retrieved {len(docs)} documents.")
    for i, doc in enumerate(docs):
        print(f"\n--- Doc {i+1} ---")
        print(doc.page_content)
