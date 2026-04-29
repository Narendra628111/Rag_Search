from git import Repo
import os

def clone_repo(repo_url: str) -> str:
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    base_dir = os.path.join("data", "repos")

    os.makedirs(base_dir, exist_ok=True)

    repo_path = os.path.join(base_dir, repo_name)

    if not os.path.exists(repo_path):
        Repo.clone_from(repo_url, repo_path)

    return repo_path, repo_name