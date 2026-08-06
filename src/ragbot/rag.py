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
def _get_llm_client():
    """Return an LLM client based on configured provider (ollama or groq)."""
    if settings.llm_provider.lower() == "ollama":
        from openai import OpenAI

        return OpenAI(
            base_url=settings.ollama_base_url,
            api_key="ollama",  # Ollama local server does not require an API key
            timeout=300.0,  # 5 minutes timeout for local inference
        )
    else:
        from groq import Client

        client_args = {}
        if settings.groq_api_key:
            client_args["api_key"] = settings.groq_api_key
        if settings.groq_base_url:
            client_args["base_url"] = settings.groq_base_url
        return Client(**client_args)


def _get_model_name() -> str:
    if settings.llm_provider.lower() == "ollama":
        return settings.ollama_model
    return settings.groq_model


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
            {
                "role": "system",
                "content": "Answer using ONLY the context below. If the answer isn't there, say you don't know.",
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": "You are a financial analyst assistant. Answer the question clearly. If you are not sure, say you don't know.",
            },
            {"role": "user", "content": question},
        ]

    client = _get_llm_client()
    model_name = _get_model_name()

    response = client.chat.completions.create(
        model=model_name,
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


def ask_stream(question: str, k: int | None = None):
    """Stream answer tokens in real-time. Yields (token_chunk, chunks)."""
    chunks = retrieve(question, k)

    if chunks:
        context = "\n\n".join(chunks)
        messages = [
            {
                "role": "system",
                "content": "Answer concisely using ONLY the context below. Keep response short and direct.",
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer concisely. If not sure, say you don't know.",
            },
            {"role": "user", "content": question},
        ]

    client = _get_llm_client()
    model_name = _get_model_name()

    stream = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content, chunks
