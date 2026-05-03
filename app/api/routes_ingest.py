
import json
import pathlib
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, field_validator
from app.services.github_service import clone_repo
from app.services.vector_service import ingest_codebase

class RepoRequest(BaseModel):
    repo_url: str

    @field_validator("repo_url")
    @classmethod
    def must_be_github(cls, v):
        v = v.strip().rstrip("/")
        if not v:
            raise ValueError("repo_url cannot be empty")
        if "github.com" not in v:
            raise ValueError("Only GitHub URLs are supported")
        return v

router = APIRouter()

STATUS_FILE = pathlib.Path("data/ingest_status.json")

def _load_status() -> dict:
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {}

def _save_status(status: dict):
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(status, indent=2))

ingest_status = _load_status()  # load from disk on startup

def _run_ingest(repo_url: str):
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    ingest_status[repo_name] = "processing"
    _save_status(ingest_status)
    try:
        repo_path, repo_name = clone_repo(repo_url)
        file_count = ingest_codebase(repo_path, repo_name)
        ingest_status[repo_name] = f"done — {file_count} files"
    except Exception as e:
        ingest_status[repo_name] = f"error: {str(e)}"
        raise  # re-raise so it still appears in server logs
    finally:
        _save_status(ingest_status)


@router.post("/ingest")
async def ingest_repo(request: RepoRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_ingest, request.repo_url)
    repo_name = request.repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    return {
        "message": "Ingestion started in background",
        "repo": repo_name,
        "status": "processing"
    }

@router.get("/ingest/status/{repo_name}")
async def get_status(repo_name: str):
    return {"repo": repo_name, "status": ingest_status.get(repo_name, "not started")}