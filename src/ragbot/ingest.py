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


def load_documents(data_dir: str) -> list[tuple[str, dict]]:
    """Load raw text and metadata from supported files in the data directory.

    Supports .txt and .md out of the box; .pdf via pypdf.
    Attaches sidecar JSON metadata if present.
    """
    import json
    from pypdf import PdfReader

    results: list[tuple[str, dict]] = []
    root = Path(data_dir)
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        meta: dict = {"source": str(path.relative_to(root))}
        sidecar_json = path.with_suffix(".json")
        if sidecar_json.exists():
            try:
                sidecar_data = json.loads(sidecar_json.read_text(encoding="utf-8"))
                meta.update(sidecar_data)
            except Exception:
                pass

        if path.suffix.lower() in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if text.strip():
                results.append((text, meta))
        elif path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if text.strip():
                results.append((text, meta))

    return results


def main() -> None:
    import argparse
    import chromadb
    from sentence_transformers import SentenceTransformer

    parser = argparse.ArgumentParser(description="Ingest documents into ChromaDB.")
    parser.add_argument("--reset", action="store_true", help="Reset/clear the Chroma collection before ingesting")
    args = parser.parse_args()

    embedder = SentenceTransformer(settings.embed_model)
    client = chromadb.PersistentClient(path=settings.chroma_path)

    if args.reset:
        try:
            client.delete_collection(settings.collection)
            print(f"Cleared existing collection {settings.collection!r}.")
        except Exception:
            pass

    collection = client.get_or_create_collection(settings.collection)

    doc_entries = load_documents(settings.data_dir)
    if not doc_entries:
        print(f"No documents found in {settings.data_dir!r}. Add some files and re-run.")
        return

    total_chunks = 0
    for doc_text, meta in doc_entries:
        source_tag = meta.get("source", "file")
        ticker = meta.get("ticker", "")
        form = meta.get("form_type", "")
        
        if ticker or form:
            prefix = f"[{ticker} {form} {source_tag}] "
        else:
            prefix = f"[Document: {source_tag}] "

        chunks = chunk_text(doc_text, settings.chunk_size, settings.chunk_overlap)
        for c_idx, chunk in enumerate(chunks):
            full_chunk = prefix + chunk
            chunk_id = f"{source_tag}:{c_idx}"
            collection.upsert(
                documents=[full_chunk],
                embeddings=[embedder.encode(full_chunk).tolist()],
                metadatas=[meta],
                ids=[chunk_id],
            )
            total_chunks += 1

    print(f"Successfully ingested {total_chunks} chunks into collection {settings.collection!r}.")


if __name__ == "__main__":
    main()
