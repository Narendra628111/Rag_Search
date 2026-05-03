
from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from app.services.vector_service import search_similar_code
from app.services.rerank_service import rerank
from app.services.llm_service import generate_answer


router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    repo_name: str

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError("query cannot be empty")
        if len(v) > 1000:
            raise ValueError("query is too long (max 1000 characters)")
        return v.strip()

    @field_validator("repo_name")
    @classmethod
    def repo_not_empty(cls, v):
        if not v.strip():
            raise ValueError("repo_name cannot be empty")
        return v.strip()


@router.post("/ask")
async def ask_question(request: QueryRequest):
    raw_results = search_similar_code(request.query, request.repo_name, limit=20)
    results = rerank(request.query, raw_results, top_k=5)

   
    if not results:
        return {"question": request.query, "answer": "Not found in codebase.", "sources": []}

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