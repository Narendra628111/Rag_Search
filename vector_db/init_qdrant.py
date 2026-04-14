from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

client = QdrantClient(url="http://localhost:6333")

client.recreate_collection(
    collection_name="codebase",
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE
    )
)

print("✅ Qdrant collection created")
