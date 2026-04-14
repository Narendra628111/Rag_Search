from fastapi import FastAPI

from app.api.routes_search import router as search_router
from app.api.routes_rag import router as rag_router

app = FastAPI(
    title="RAG Code Search API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "API is running 🚀"}

app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(rag_router, prefix="/rag", tags=["RAG"])