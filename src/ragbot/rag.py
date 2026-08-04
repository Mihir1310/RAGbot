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

NO_CONTEXT_PROMPT_TEMPLATE = """You are a helpful assistant. Answer the question directly. \
If you are not sure, say you don't know.

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


@lru_cache(maxsize=1)
def _get_groq_client():
    from groq import Client

    client_args = {}
    if settings.groq_api_key:
        client_args["api_key"] = settings.groq_api_key
    if settings.groq_base_url:
        client_args["base_url"] = settings.groq_base_url
    return Client(**client_args)


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
    chunks = retrieve(question, k)

    if chunks:
        context = "\n\n".join(chunks)
        messages = [
            {"role": "system", "content": "Answer using ONLY the context below. If the answer isn't there, say you don't know."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
    else:
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer the question directly. If you are not sure, say you don't know."},
            {"role": "user", "content": question},
        ]

    response = _get_groq_client().chat.completions.create(
        model=settings.groq_model,
        messages=messages,
    )

    first_choice = response.choices[0]
    message = first_choice.message
    content = message.content
    if isinstance(content, str):
        answer = content
    elif hasattr(content, "__iter__"):
        answer = "".join(
            part.text if hasattr(part, "text") else str(part)
            for part in content
        )
    else:
        answer = str(content)

    return answer, chunks
