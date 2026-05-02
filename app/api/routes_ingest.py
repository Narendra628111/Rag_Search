from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services.github_service import clone_repo
from app.services.vector_service import ingest_codebase

router = APIRouter()

class RepoRequest(BaseModel):
    repo_url: str

def _run_ingest(repo_url: str):
    """Runs in the background — not in the async event loop."""
    repo_path, repo_name = clone_repo(repo_url)
    file_count = ingest_codebase(repo_path, repo_name)
    print(f"[ingest] Done: {repo_name} — {file_count} files")

@router.post("/ingest")
async def ingest_repo(request: RepoRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_ingest, request.repo_url)
    repo_name = request.repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    return {
        "message": "Ingestion started in background",
        "repo": repo_name,
        "status": "processing"
    }