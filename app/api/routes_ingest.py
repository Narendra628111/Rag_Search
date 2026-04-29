from fastapi import APIRouter
from pydantic import BaseModel
from app.services.github_service import clone_repo
from app.services.vector_service import ingest_codebase

router = APIRouter()

class RepoRequest(BaseModel):
    repo_url: str

@router.post("/ingest")
async def ingest_repo(request: RepoRequest):

    repo_path, repo_name = clone_repo(request.repo_url)

    ingest_codebase(repo_path, repo_name)

    return {
        "message": "Repository ingested successfully",
        "repo": repo_name
    }