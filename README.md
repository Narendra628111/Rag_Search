# RAG Search — Codebase Q&A

> Ask natural-language questions about any GitHub repository and get precise, context-aware answers — powered by local embeddings and Google Gemini.

---

## How it works

```
GitHub Repo URL
      │
      ▼
 git clone ──► tree-sitter AST chunking ──► all-MiniLM-L6-v2 (local) ──► Qdrant (vector store)
                                                                                    │
 Your Question ──► embed query ─────────────────────────────────► vector search (top 20)
                                                                                    │
                                                                         cosine rerank (top 5)
                                                                                    │
                                                                                    ▼
                                                                    Gemini (gemini-3-flash-preview)
                                                                                    │
                                                                                    ▼
                                                                               Answer + Sources
```

**Two flows:**

**Ingest** — You provide a GitHub URL. The server clones the repo into `data/repos/`, walks every file, parses Python/JS/TS files with tree-sitter at the function and class level (all other file types use a sliding window fallback), embeds every chunk locally using `all-MiniLM-L6-v2`, and upserts them into Qdrant in batches of 100. Runs entirely in the background — the API returns immediately.

**Query** — You provide a question and a repo name. The server embeds your question with the same local model, searches Qdrant for the top 20 most similar chunks filtered to that repo, reranks them by exact cosine similarity to get the top 5, builds a context string, and sends it to Gemini to generate the final answer.

---

## Prerequisites

- Python 3.11+
- Qdrant running locally
- A Gemini API key → [Get one here](https://aistudio.google.com/app/apikey)

---

## Setup

### 1. Start Qdrant

**Windows — using qdrant.exe:**
```bash
# Download qdrant.exe from https://github.com/qdrant/qdrant/releases
# Open Command Prompt in the folder where you saved it and run:
.\qdrant.exe
```

Qdrant will start at `http://localhost:6333`. You can confirm it's running by opening that URL in your browser — you should see the Qdrant dashboard.

### 2. Clone this repo and install dependencies

```bash
git clone https://github.com/Narendra628111/Rag_Search.git
cd rag-search
pip install -r requirements.txt
```

> The first run will download `all-MiniLM-L6-v2` (~90MB) automatically. After that it is cached locally — no internet needed for embeddings.

### 3. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
GEMINI_API_KEY=your-gemini-api-key-here
GENERATION_MODEL=gemini-3-flash-preview
EMBEDDING_MODEL=all-MiniLM-L6-v2
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=codebase
```

> **Important:** Do NOT change `EMBEDDING_MODEL` after ingesting repos. The query embedding must use the same model as ingestion — if they differ, similarity search will return garbage results. If you ever change the model, update `VECTOR_SIZE` in `vector_service.py` to match and re-ingest all repos from scratch.

### 4. Start the server

```bash
# using uvicorn directly
uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`
Interactive API docs at `http://localhost:8000/docs`

---

## API Reference

### POST `/api/ingest` — Ingest a repository

Clones and indexes the repository in the background. Returns immediately without waiting for ingestion to complete.

**Request:**
```json
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

**Validation:**
- `repo_url` must be a valid GitHub URL (`github.com` must be present)
- Empty URLs return a `422` error

---

### GET `/api/ingest/status/{repo_name}` — Check ingest status

Poll this after calling `/api/ingest` to know when the repo is ready to query.

**Example:**
```
GET /api/ingest/status/fastapi
```

**Response:**
```json
{
  "repo": "fastapi",
  "status": "done — 42 files"
}
```

**Possible status values:**

| Status | Meaning |
|---|---|
| `not started` | Repo has never been ingested |
| `processing` | Currently cloning and embedding |
| `done — N files` | Ingestion complete, N files indexed |
| `error: <message>` | Ingestion failed — message explains why |

> Status is persisted to `data/ingest_status.json` — survives server restarts.

---

### POST `/api/ask` — Ask a question about a repo

**Request:**
```json
{
  "query": "How does authentication work?",
  "repo_name": "repo"
}
```

**Response:**
```json
{
  "question": "How does authentication work?",
  "answer": "Authentication is handled by the verify_token() function in app/auth/token.py ...",
  "sources": [
    { "file": "data/repos/repo/app/auth/token.py", "score": 0.9123 },
    { "file": "data/repos/repo/app/middleware.py", "score": 0.8741 }
  ]
}
```

**Validation:**
- `query` cannot be empty and must be under 1000 characters
- `repo_name` cannot be empty
- Invalid input returns a `422` error

**If nothing is found:**
```json
{
  "question": "...",
  "answer": "Not found in codebase.",
  "sources": []
}
```

---

## Example — Full walkthrough using curl

```bash
# Step 1 — Ingest a repo (runs in background)
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d "{\"repo_url\": \"https://github.com/tiangolo/fastapi\"}"

# Step 2 — Poll until status is "done"
curl http://localhost:8000/api/ingest/status/fastapi

# Step 3 — Ask a question
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"How does dependency injection work?\", \"repo_name\": \"fastapi\"}"
```

---

## Project Structure

```
rag-search/
│
├── main.py                        ← Entrypoint — runs uvicorn programmatically
│
├── app/
│   ├── main.py                    ← FastAPI app, router registration
│   │
│   ├── core/
│   │   └── config.py              ← Pydantic settings — reads all values from .env
│   │
│   ├── api/
│   │   ├── routes_ingest.py       ← POST /api/ingest, GET /api/ingest/status/{repo}
│   │   └── routes_rag.py          ← POST /api/ask
│   │
│   └── services/
│       ├── embedding_service.py   ← Loads all-MiniLM-L6-v2 once, exposes get_embedding()
│       │                            and get_embeddings_batch() — single source of truth
│       ├── chunker_service.py     ← tree-sitter AST chunking for .py/.js/.ts,
│       │                            sliding window fallback for everything else
│       ├── vector_service.py      ← Qdrant collection management, batched upsert,
│       │                            cosine similarity search filtered by repo
│       ├── rerank_service.py      ← Batched cosine reranking: top-20 → top-5
│       ├── llm_service.py         ← Gemini answer generation with structured prompt
│       └── github_service.py      ← git clone into data/repos/, skips if already exists
│
├── data/                          ← Auto-created at runtime
│   ├── repos/                     ← Cloned repositories
│   └── ingest_status.json         ← Persisted ingest status (survives restarts)
│
├── .env                           ← Your secrets (not committed)
├── .env.example                   ← Template — copy this to .env
├── requirements.txt
└── .gitignore
```

---

## Supported File Types

| Type | Extensions | Chunking strategy |
|---|---|---|
| Python | `.py` | tree-sitter — function + class level |
| JavaScript | `.js` | tree-sitter — function + class level |
| TypeScript | `.ts` | tree-sitter — function + class level |
| Markdown, Text, JSON, SQL | `.md` `.txt` `.json` `.sql` | Sliding window (500 chars, 50 overlap) |

Files matching these patterns are skipped entirely: `node_modules/`, `venv/`, `__pycache__/`, `dist/`, `build/`, `.git/`, `*.min.js`, `*.min.css`, `vendor`, `jquery`, `bootstrap`, `lodash`, `moment`.

---

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| API framework | FastAPI | Async, automatic docs, Pydantic validation |
| Embeddings | `all-MiniLM-L6-v2` via SentenceTransformers | Runs locally — no API cost, no latency |
| Vector database | Qdrant | Native cosine similarity, metadata filtering by repo |
| Code parsing | tree-sitter | AST-level chunking — complete functions, not arbitrary slices |
| LLM | Google Gemini (`gemini-3-flash-preview`) | Answer generation from retrieved context |
| Reranking | scikit-learn cosine similarity | Two-stage retrieval: fast ANN search → exact rerank |
| Repo cloning | GitPython | Pure Python git clone |

---

## Known Limitations

- Only public GitHub repositories are supported
- Large repos (1000+ files) can take several minutes to ingest on first run
