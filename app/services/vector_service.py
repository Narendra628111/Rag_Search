from qdrant_client import QdrantClient
from app.core.config import settings
from app.services.embedding_service import get_embedding

client = QdrantClient(url=settings.QDRANT_URL)

def search_similar_code(query: str, top_k: int = 5):
    query_vector = get_embedding(query)

    results = client.search(
        collection_name=settings.COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )

    return results