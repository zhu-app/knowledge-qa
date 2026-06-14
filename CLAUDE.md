# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A local knowledge-base Q&A system built on **RAG (Retrieval-Augmented Generation)** architecture with a Streamlit web UI. Users upload documents (PDF/Markdown/TXT) or web pages, which are chunked, embedded, and indexed in a FAISS vector store. Queries are answered by retrieving relevant chunks and passing them as context to an LLM.

## Directory Structure

```
knowledge-qa/
├── app.py                          # Streamlit main application (UI + chat + file upload)
├── knowledge_qa/                   # Core library
│   ├── config.py                   # .env loading, API keys, model config, validation
│   ├── loader.py                   # Document loaders: PDF, Markdown, TXT, web page
│   ├── splitter.py                 # Text chunking via RecursiveCharacterTextSplitter
│   ├── vector_store.py             # FAISS vector store: build, save, load, merge (singleton embeddings)
│   └── qa_chain.py                 # LLM wrapper, prompt builder, QAChat class (stream + invoke)
├── data/faiss_index/               # Persisted FAISS index (auto-created on first upload)
├── .env                            # Runtime config (API keys, model endpoints) — git-ignored
├── .env.example                    # Template for .env
├── requirements.txt                # Python dependencies
├── setup.bat                       # One-click install: venv + pip install (Tsinghua mirror)
└── start.bat                       # Launch Streamlit on :8501
```

## Key Architecture Decisions

- **Embeddings**: Uses `FastEmbedEmbeddings` with `BAAI/bge-small-zh-v1.5` (singleton pattern, downloaded once). Hugging Face mirror (`hf-mirror.com`) set for mainland China.
- **Vector store**: FAISS, persisted to `data/faiss_index/`. New uploads merge into existing index via `merge_vector_stores()`.
- **LLM**: Abstracted via `ChatOpenAI` (OpenAI-compatible API). Supports any provider with OpenAI-compatible endpoints (OpenAI, Zhipu GLM, DeepSeek, Qwen, etc.) configured through `.env`.
- **Retrieval**: `similarity_search_with_relevance_scores` with k=4, filtered by `SIMILARITY_THRESHOLD` (default 0.5).
- **Streaming**: LLM responses are streamed chunk-by-chunk to the UI via a generator.
- **Conversation history**: Last 6 messages kept in context; full history passed to LLM prompt as text.

## Common Commands

```powershell
# Install dependencies
.\setup.bat

# Start the app
.\start.bat          # Opens http://localhost:8501

# Manual start (if already in venv)
venv\Scripts\python.exe -m streamlit run app.py --server.port 8501

# Activate venv manually (PowerShell)
.\venv\Scripts\Activate.ps1
```

## Configuration

All config lives in `.env` (copy from `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | (required) | API key for LLM |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible endpoint |
| `LLM_MODEL` | `gpt-4o-mini` | Model name |
| `EMBEDDING_MODEL` | `embedding-2` | Embedding model name (metadata only, actual model is hardcoded) |
| `SIMILARITY_THRESHOLD` | `0.5` | Min relevance score to keep retrieved chunks (0.0~1.0) |

`config.py` validates `OPENAI_API_KEY` at import time and exits if missing.

## Implementation Notes

- `knowledge_qa/__init__.py` is empty — no package-level exports.
- `loader.py` writes uploaded files to a temp file on disk before loading (needed by `pdfplumber` and `TextLoader`).
- `vector_store.py` uses a module-level `_embeddings` singleton to avoid re-downloading the model.
- `qa_chain.py`'s `QAChat` class is stateless except for the LLM instance; instantiated per-session in `st.session_state["qa_chain"]`.
- The Streamlit app manages state via `st.session_state`: `messages`, `vector_store`, `qa_chain`.
