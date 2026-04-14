from ingestion.repo_loader import load_repo
from ingestion.chunker import chunk_code
from embeddings.embedder import get_embedding
from vector_db.client import client
import time
import uuid

COLLECTION_NAME = "codebase"

import uuid
from ingestion.repo_loader import load_repo
from ingestion.chunker import chunk_code
from embeddings.embedder import get_embedding
from vector_db.client import client

COLLECTION_NAME = "codebase"

def run(repo_url: str):
    print("🚀 Starting ingestion...")

    # Step 1: Load repo
    files = load_repo(repo_url)
    print(f"📂 Loaded {len(files)} files")

    if not files:
        print("❌ No files found. Check repo_loader.")
        return

    # Step 2: Chunk code
    chunks = chunk_code(files)
    print(f"🧩 Created {len(chunks)} chunks")

    if not chunks:
        print("❌ No chunks created. Check chunker.")
        return

    points = []

    # Step 3: Embed + store
    for i, chunk in enumerate(chunks):
        vector = get_embedding(chunk["code"])

        points.append({
            "id": str(uuid.uuid4()),
            "vector": vector,
            "payload": {
                "file_path": chunk["file_path"],
                "code": chunk["code"]
            }
        })

        # Debug progress
        if i % 50 == 0:
            print(f"⚡ Processed {i} chunks")

    # Step 4: Store in Qdrant
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(f"✅ Stored {len(points)} chunks in Qdrant")


if __name__ == "__main__":
    repo_url = "https://github.com/pallets/flask"
    run(repo_url)