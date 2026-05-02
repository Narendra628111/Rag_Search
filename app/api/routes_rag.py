
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.vector_service import search_similar_code
from app.services.rerank_service import rerank
from app.services.llm_service import generate_answer

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    repo_name: str

@router.post("/ask")
async def ask_question(request: QueryRequest):
    # Fetch wider candidate set
    raw_results = search_similar_code(request.query, request.repo_name, limit=10)

    # Rerank with cosine similarity, keep top-5
    results = rerank(request.query, raw_results, top_k=5)

    context = "\n\n".join([r.payload["content"] for r in results])
    answer = generate_answer(request.query, context)

    return {
        "question": request.query,
        "answer": answer,
        "sources": [
            {"file": r.payload["file_path"], "score": r.score}
            for r in results
        ]
    }