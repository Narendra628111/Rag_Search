
from fastapi import FastAPI
from app.api import routes_rag, routes_ingest

app = FastAPI(
    title="RAG Search — Codebase Q&A",
    description="Ask natural-language questions about any GitHub repository.",
    version="0.1.0",
)

app.include_router(routes_ingest.router, prefix="/api")
app.include_router(routes_rag.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}