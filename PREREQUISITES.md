# Prerequisites & Tech Stack

A reference for anyone (including future-you) picking up RAGbot. Read/install these before diving into the code.

## Core concepts to know

| Concept | Why it matters here |
|---|---|
| **RAG (Retrieval-Augmented Generation)** | The core architecture: retrieve relevant text chunks, then feed them to an LLM as context instead of relying on its trained knowledge. |
| **Embeddings & vector similarity** | Documents/questions are converted to vectors; retrieval works by finding the nearest vectors (cosine/L2 distance). |
| **Chunking & overlap** | Long documents are split into small overlapping pieces so retrieval is precise and fits in the model's context window. |
| **LoRA (Low-Rank Adaptation)** | A parameter-efficient fine-tuning method — trains small adapter matrices instead of the full model, making CPU fine-tuning feasible. |
| **Quantization (Q4, Q8, etc.)** | Compressed model weights that trade a little quality for much faster CPU inference and lower memory use. |

## Required installs

| Tool | Purpose | Install |
|---|---|---|
| [Python 3.12+](https://www.python.org/downloads/) | Language runtime | — |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Python package/dependency manager (used instead of raw pip) | `pip install uv` or see docs |
| [Ollama](https://ollama.com/download) | Runs small LLMs locally on CPU, no GPU needed | Download installer for your OS |
| [Git](https://git-scm.com/downloads) | Version control | Download installer |

After installing Ollama, pull the default model used by this project:

```bash
ollama pull qwen2.5:3b
ollama run qwen2.5:3b "Say hello in one sentence."
```

## Python libraries (installed via `uv sync`)

| Library | Role |
|---|---|
| [chromadb](https://docs.trychroma.com) | Local vector database for storing/querying document embeddings |
| [sentence-transformers](https://sbert.net) | Generates embeddings locally (`all-MiniLM-L6-v2`, ~80MB) |
| [streamlit](https://streamlit.io) | Chat UI, pure Python |
| [ollama (python client)](https://github.com/ollama/ollama-python) | Talks to the local Ollama server from Python |
| [pypdf](https://pypdf.readthedocs.io) | Extracts text from PDF source documents |
| [pydantic](https://docs.pydantic.dev) / pydantic-settings | Typed config and data models |

### Week 2 only — fine-tuning extras (`uv sync --extra finetune`)

| Library | Role |
|---|---|
| [transformers](https://huggingface.co/docs/transformers) | Loads/runs the base Hugging Face model |
| [peft](https://huggingface.co/docs/peft) | LoRA fine-tuning implementation |
| [datasets](https://huggingface.co/docs/datasets) | Loads/formats the JSONL training data |
| [accelerate](https://huggingface.co/docs/accelerate) | Handles training loop device placement (CPU here) |

## Suggested learning order

1. Skim what RAG is and why grounding answers in retrieved context reduces hallucination.
2. Read the [ChromaDB quickstart](https://docs.trychroma.com/getting-started) — add, query, embeddings basics.
3. Read the [Sentence Transformers quickstart](https://www.sbert.net/docs/quickstart.html).
4. Try `ollama run <model>` a few times to get a feel for local inference speed/limits.
5. (Week 2 only) Skim the [PEFT LoRA docs](https://huggingface.co/docs/peft/conceptual_guides/lora) before touching fine-tuning code.

## Environment setup checklist

```bash
git clone <your-repo-url>
cd RAGbot
uv sync                 # installs core dependencies
cp .env.example .env    # copy and adjust config
ollama pull qwen2.5:3b  # pull the local model
```

See [README.md](README.md) for how to run ingestion and the chat UI, and [docs/local-ml-project-guide.html](docs/local-ml-project-guide.html) for the full day-by-day build guide.
