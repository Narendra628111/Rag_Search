# RAG Search — Codebase Q&A

Ask natural-language questions about any Git repository. 
Uses tree-sitter for function-level chunking, sentence-transformers for 
local embeddings, Qdrant as the vector store, cosine reranking, and 
Gemini for answer generation.

## Prerequisites

- Python 3.11+
- [Qdrant](https://qdrant.tech/documentation/quick-start/) running locally:
```bash
  docker run -p 6333:6333 qdrant/qdrant
```

## Setup

```bash
cp .env.example .env        # fill in GEMINI_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API

### Ingest a repo (async — returns immediately)
POST /ingest
{ "repo_url": "https://github.com/user/repo" }

### Ask a question
POST /ask
{ "query": "How does authentication work?", "repo_name": "repo" }

## Architecture
app/
api/
routes_ingest.py   ← clone + background ingest
routes_rag.py      ← search + rerank + LLM
services/
chunker_service.py ← tree-sitter function extraction
embedding_service.py ← SentenceTransformer (single source)
github_service.py  ← git clone
llm_service.py     ← Gemini generation
rerank_service.py  ← cosine reranking top-10 → top-5
vector_service.py  ← Qdrant upsert + search

