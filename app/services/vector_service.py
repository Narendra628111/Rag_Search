import os
import uuid
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

# 🔥 Load model once (VERY IMPORTANT)
model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔹 Embedding function
def get_embedding(text: str) -> List[float]:
    return model.encode(text).tolist()


# 🔹 Qdrant setup
qdrant_client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "codebase"


# 🔹 Create collection (FIXED SIZE = 384)
def create_collection():
    collections = qdrant_client.get_collections().collections
    existing = [c.name for c in collections]

    if COLLECTION_NAME in existing:
        qdrant_client.delete_collection(COLLECTION_NAME)  # clean reset

    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,  # ✅ MiniLM dimension
            distance=Distance.COSINE
        )
    )


# 🔹 Store embedding
def store_embedding(content: str, file_path: str, repo_name: str):
    vector = get_embedding(content)

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            {
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {
                    "content": content,
                    "file_path": file_path,
                    "repo": repo_name
                }
            }
        ]
    )


# 🔹 Ingest repo
def ingest_codebase(folder_path: str, repo_name: str):
    create_collection()

    file_count = 0

    for root, dirs, files in os.walk(folder_path):

        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "venv", "__pycache__"]]

        for file in files:
            if file.endswith((".py", ".js", ".ts", ".md", ".txt", ".json",".sql")):

                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception:
                    continue

                # 🔹 Smaller chunks = better embeddings
                chunks = [
                    content[i:i + 300]
                    for i in range(0, len(content), 300)
                ]

                for chunk in chunks:
                    store_embedding(chunk, file_path, repo_name)

                file_count += 1

    return file_count


# 🔹 Search
def search_similar_code(query: str, repo_name: str, limit: int = 5):
    query_vector = get_embedding(query)

    results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        query_filter={
            "must": [
                {
                    "key": "repo",
                    "match": {"value": repo_name}
                }
            ]
        }
    )

    return results