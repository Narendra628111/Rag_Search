from fastapi import APIRouter
from pydantic import BaseModel
from app.services.vector_service import search_similar_code
from app.services.llm_service import generate_answer

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    repo_name: str   # 🔥 NEW

@router.post("/ask")
async def ask_question(request: QueryRequest):

    results = search_similar_code(request.query, request.repo_name)

    for r in results:
        print("FILE:", r.payload["file_path"])
        print("CONTENT:", r.payload["content"][:200])
        print("SCORE:", r.score)
        print("="*50)

    context = "\n\n".join([
        r.payload["content"][:300] for r in results
    ])

    answer = generate_answer(request.query, context)

    return {
        "question": request.query,
        "answer": answer,
        "sources": [
            {
                "file": r.payload["file_path"],
                "score": r.score
            }
            for r in results
        ]
    }