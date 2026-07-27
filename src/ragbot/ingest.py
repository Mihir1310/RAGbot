"""Document ingestion: load files, chunk text, embed, and store in Chroma.

Week 1, Days 1-2. Run with: `uv run ragbot-ingest`
"""

from pathlib import Path

from .config import settings


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def load_documents(data_dir: str) -> list[str]:
    """Load raw text from supported files in the data directory.

    Supports .txt and .md out of the box; .pdf via pypdf.
    """
    from pypdf import PdfReader

    texts: list[str] = []
    root = Path(data_dir)
    for path in root.rglob("*"):
        if path.suffix.lower() in {".txt", ".md"}:
            texts.append(path.read_text(encoding="utf-8", errors="ignore"))
        elif path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            texts.append("\n".join(page.extract_text() or "" for page in reader.pages))
    return texts


def main() -> None:
    import chromadb
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(settings.embed_model)
    client = chromadb.PersistentClient(path=settings.chroma_path)
    collection = client.get_or_create_collection(settings.collection)

    documents = load_documents(settings.data_dir)
    if not documents:
        print(f"No documents found in {settings.data_dir!r}. Add some files and re-run.")
        return

    idx = 0
    for doc in documents:
        for chunk in chunk_text(doc, settings.chunk_size, settings.chunk_overlap):
            collection.add(
                documents=[chunk],
                embeddings=[embedder.encode(chunk).tolist()],
                ids=[f"chunk-{idx}"],
            )
            idx += 1

    print(f"Ingested {idx} chunks into collection {settings.collection!r}.")


if __name__ == "__main__":
    main()
