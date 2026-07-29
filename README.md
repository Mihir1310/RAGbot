# RAGbot

A local, **CPU-only** retrieval-augmented (RAG) assistant over your own documents,
plus a Week 2 LoRA fine-tune experiment. No GPU required, models ≤ 3B params.

See the full build guide in [docs/local-ml-project-guide.html](docs/local-ml-project-guide.html), and [PREREQUISITES.md](PREREQUISITES.md) for the tech stack, concepts, and installs to review beforehand.

## Stack

- **Runtime:** [Groq API](https://www.groq.ai) (hosted generation)
- **Embeddings:** [Sentence Transformers](https://sbert.net) (`all-MiniLM-L6-v2`)
- **Vector store:** [ChromaDB](https://docs.trychroma.com)
- **UI:** [Streamlit](https://streamlit.io)
- **Packaging:** [uv](https://docs.astral.sh/uv/)

## Project structure

```
RAGbot/
├── src/ragbot/
│   ├── config.py     # env-based settings (Pydantic)
│   ├── ingest.py     # load → chunk → embed → store in Chroma
│   ├── rag.py        # retrieve + generate (the core RAG loop)
│   └── app.py        # Streamlit chat UI
├── tests/
├── data/             # your source documents (gitignored)
├── docs/             # the project guide
├── .env.example
└── pyproject.toml
```

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Configure
cp .env.example .env

# 3. Set your Groq API key in .env
#    RAGBOT_GROQ_API_KEY=your_groq_api_key_here

# 4. Add documents to ./data (.txt, .md, .pdf)
```

## Usage

```bash
# Ingest documents into the vector store
uv run ragbot-ingest

# Launch the chat UI
uv run streamlit run src/ragbot/app.py
```

## Roadmap

- **Week 1** — RAG assistant: ingest → retrieve → generate → UI ✅ scaffolded
- **Week 2** — LoRA fine-tune a small model's style, then benchmark
  (install extras: `uv sync --extra finetune`)

## Development

```bash
uv run pytest -v          # tests
uv run ruff format .      # format
uv run ruff check --fix . # lint
```
