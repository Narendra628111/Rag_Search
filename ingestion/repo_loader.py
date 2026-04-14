import os
import git

def load_repo(repo_url: str, clone_dir="data/repos/repo"):
    # Clone if not exists
    if not os.path.exists(clone_dir):
        git.Repo.clone_from(repo_url, clone_dir)
        print(f"Cloned to {clone_dir}")
    else:
        print("Repo already exists")

    files = []

    for root, _, filenames in os.walk(clone_dir):
        for file in filenames:
            if file.endswith(".py"):  # you can extend later
                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        files.append({
                            "file_path": path,
                            "content": f.read()
                        })
                except:
                    pass  # skip unreadable files

    return files