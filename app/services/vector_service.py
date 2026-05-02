# app/services/vector_service.py
#
# Responsibilities: Qdrant collection management, storing vectors, searching.
#
# Embedding is intentionally NOT done here.
# Import get_embedding from embedding_service — that is the single source of truth.

import os
import uuid
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.core.config import settings
from app.services.embedding_service import get_embedding  # ← single source of truth

# Qdrant client — reads URL from .env via settings
qdrant_client = QdrantClient(url=settings.QDRANT_URL)

COLLECTION_NAME = settings.COLLECTION_NAME

# Dimension must match the embedding model.
# all-MiniLM-L6-v2 → 384. If you change EMBEDDING_MODEL in .env,
# update this value to match and re-ingest all repos.
VECTOR_SIZE = 384


def create_collection() -> None:
    """
    Create the Qdrant collection if it does not already exist.
    Safe to call on every ingest — will NOT delete existing data.
    """
    existing = [c.name for c in qdrant_client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )


def store_embedding(content: str, file_path: str, repo_name: str) -> None:
    """
    Embed a single chunk and upsert it into Qdrant.
    Uses get_embedding() from embedding_service — same model as search.
    """
    vector = get_embedding(content)

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "content": content,
                    "file_path": file_path,
                    "repo": repo_name,
                },
            )
        ],
    )


def ingest_codebase(folder_path: str, repo_name: str) -> int:
    create_collection()

    all_chunks = []   # collect everything first

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "venv", "__pycache__"}]

        for file in files:
            if not file.endswith((".py", ".js", ".ts", ".md", ".txt", ".json", ".sql")):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            chunks = [content[i:i + 300] for i in range(0, len(content), 300)]
            for chunk in chunks:
                if chunk.strip():
                    all_chunks.append({"content": chunk, "file_path": file_path})

    # Embed all chunks in one batched call
    if all_chunks:
        from app.services.embedding_service import get_embeddings_batch
        texts = [c["content"] for c in all_chunks]
        vectors = get_embeddings_batch(texts)

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vectors[i],
                payload={"content": all_chunks[i]["content"],
                         "file_path": all_chunks[i]["file_path"],
                         "repo": repo_name}
            )
            for i in range(len(all_chunks))
        ]

        # Upsert in batches of 100
        for i in range(0, len(points), 100):
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points[i:i + 100]
            )

    return len({c["file_path"] for c in all_chunks})


def search_similar_code(query: str, repo_name: str, limit: int = 5) -> list:
    """
    Embed the query and search Qdrant for the closest chunks in the given repo.
    Uses get_embedding() from embedding_service — same model as ingestion.
    """
    query_vector = get_embedding(query)

    return qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="repo",
                    match=MatchValue(value=repo_name),
                )
            ]
        ),
    )