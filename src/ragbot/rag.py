"""Retrieval + generation: the core RAG loop.

Week 1, Days 3-4.
"""

from functools import lru_cache

from .config import settings

PROMPT_TEMPLATE = """Answer using ONLY the context below. \
If the answer isn't there, say you don't know.

Context:
{context}

Question: {question}"""


@lru_cache(maxsize=1)
def _get_embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embed_model)


@lru_cache(maxsize=1)
def _get_collection():
    import chromadb

    client = chromadb.PersistentClient(path=settings.chroma_path)
    return client.get_or_create_collection(settings.collection)


def retrieve(question: str, k: int | None = None) -> list[str]:
    """Return the top-k most relevant chunks for a question."""
    k = k or settings.top_k
    q_emb = _get_embedder().encode(question).tolist()
    results = _get_collection().query(query_embeddings=[q_emb], n_results=k)
    return results["documents"][0] if results["documents"] else []


def ask(question: str, k: int | None = None) -> tuple[str, list[str]]:
    """Answer a question grounded in retrieved context.

    Returns the answer and the source chunks used.
    """
    import ollama

    chunks = retrieve(question, k)
    context = "\n\n".join(chunks)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    response = ollama.chat(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"], chunks
