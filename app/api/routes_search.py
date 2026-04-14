from fastapi import APIRouter
from pydantic import BaseModel
from app.services.vector_service import search_similar_code
from app.services.llm_service import generate_answer

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/ask")
async def ask_question(request: QueryRequest):
    # Step 1: Retrieve relevant code
    results = search_similar_code(request.query)

    # Step 2: Build context
    context = "\n\n".join([r.payload["content"] for r in results])

    # Step 3: Generate answer
    answer = generate_answer(request.query, context)

    return {
        "question": request.query,
        "answer": answer,
        "sources": [r.payload["file_path"] for r in results]
    }