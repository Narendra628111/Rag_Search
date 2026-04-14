from qdrant_client import QdrantClient
from app.core.config import settings
from app.services.embedding_service import get_embedding
import os
import uuid

client = QdrantClient(url=settings.QDRANT_URL)

COLLECTION_NAME = settings.COLLECTION_NAME


def read_code_files(folder_path):
    code_chunks = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".java")):
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                    code_chunks.append({
                        "file_path": file_path,
                        "content": content
                    })

    return code_chunks


def ingest(folder_path):
    code_chunks = read_code_files(folder_path)

    points = []

    for chunk in code_chunks:
        # ✅ Limit content size (prevents API issues)
        content = chunk["content"][:10000]

        vector = get_embedding(content)

        # ✅ Skip empty/invalid embeddings
        if vector is None:
            continue

        points.append({
            "id": str(uuid.uuid4()),
            "vector": vector,
            "payload": {
               "file_path": chunk["file_path"],
               "content": content
            }
        })

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(f"✅ Ingested {len(points)} files into Qdrant")


if __name__ == "__main__":
    # 👉 CHANGE THIS PATH to your project folder
    ingest("app/")