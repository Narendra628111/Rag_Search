# RAG Search — Codebase Q&A

> Ask natural-language questions about any GitHub repository and get precise, context-aware answers powered by local embeddings and Gemini.

---

## How it works

```
GitHub Repo
    │
    ▼
Clone  ──▶  tree-sitter chunking  ──▶  SentenceTransformer embeddings  ──▶  Qdrant (vector store)
                                                                                      │
Query ──▶  embed query ──────────────────────────────────────────────▶  vector search + cosine rerank
                                                                                      │
                                                                                      ▼
                                                                              Gemini  ──▶  Answer
```

1. **Ingest** — clones the repo, parses each file with tree-sitter into function-level chunks, embeds them locally with `all-MiniLM-L6-v2`, and stores vectors in Qdrant
2. **Query** — embeds the question, retrieves top-10 similar chunks from Qdrant, reranks by cosine similarity, and sends the top-5 to Gemini for answer generation

---

## Prerequisites

- Python 3.11+
- Docker (for Qdrant)
- A Gemini API key → [Get one here](https://aistudio.google.com/app/apikey)

---

## Setup

### 1. Start Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Then open `.env` and fill in your values:

```env
GEMINI_API_KEY=your-gemini-api-key-here
GENERATION_MODEL=gemini-2.0-flash
EMBEDDING_MODEL=all-MiniLM-L6-v2
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=codebase
```

> **Note:** The embedding model runs locally — no API key needed, no cost, no internet after the first download.
> Do **not** change `EMBEDDING_MODEL` after ingesting a repo without also updating `VECTOR_SIZE` in `vector_service.py` and re-ingesting.

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

---

## API

### Health check

```http
GET /health
```

```json
{ "status": "ok" }
```

---

### Ingest a repository

Clones and indexes the repo in the background. Returns immediately.

```http
POST /api/ingest
Content-Type: application/json

{
  "repo_url": "https://github.com/user/repo"
}
```

**Response:**
```json
{
  "message": "Ingestion started in background",
  "repo": "repo",
  "status": "processing"
}
```

---

### Check ingest status

```http
GET /api/ingest/status/{repo_name}
```

**Response:**
```json
{
  "repo": "repo",
  "status": "done — 42 files"
}
```

Possible status values: `not started` · `processing` · `done — N files` · `error: <message>`

---

### Ask a question

```http
POST /api/ask
Content-Type: application/json

{
  "query": "How does authentication work?",
  "repo_name": "repo"
}
```

**Response:**
```json
{
  "answer": "Authentication is handled by the `verify_token()` function in ...",
  "sources": [
    {
      "file": "app/auth/token.py",
      "content": "def verify_token(token: str) -> bool: ..."
    }
  ]
}
```

---

## Project structure

```
app/
├── main.py                    ← FastAPI app, router registration
├── core/
│   └── config.py              ← Pydantic settings from .env
└── api/
│   ├── routes_ingest.py       ← POST /ingest, GET /ingest/status
│   └── routes_rag.py          ← POST /ask
└── services/
    ├── chunker_service.py     ← tree-sitter function extraction + sliding window fallback
    ├── embedding_service.py   ← SentenceTransformer (single source of truth for embeddings)
    ├── github_service.py      ← git clone
    ├── llm_service.py         ← Gemini answer generation
    ├── rerank_service.py      ← cosine reranking top-10 → top-5
    └── vector_service.py      ← Qdrant upsert + similarity search
```

---

## Supported languages

Parsed at the function/class level via tree-sitter:

| Language   | Extensions      |
|------------|-----------------|
| Python     | `.py`           |
| JavaScript | `.js`           |
| TypeScript | `.ts`           |

All other file types fall back to a sliding-window chunker (500 chars, 50 char overlap).

---

## Example usage

```bash
# 1. Ingest a repo
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/tiangolo/fastapi"}'

# 2. Poll until done
curl http://localhost:8000/api/ingest/status/fastapi

# 3. Ask a question
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "How does dependency injection work?", "repo_name": "fastapi"}'
```

---

## Tech stack

| Component        | Technology                        |
|------------------|-----------------------------------|
| API framework    | FastAPI                           |
| Embeddings       | `all-MiniLM-L6-v2` (local)       |
| Vector store     | Qdrant                            |
| Code parsing     | tree-sitter                       |
| LLM              | Google Gemini                     |
| Reranking        | scikit-learn cosine similarity    |
| Repo cloning     | GitPython                         |

---

## Known limitations

- `ingest_status` is stored in memory — restarting the server resets status (repos already in Qdrant are still searchable)
- Only GitHub URLs are supported for ingestion
- Large repos (1000+ files) may take several minutes to ingest on first run