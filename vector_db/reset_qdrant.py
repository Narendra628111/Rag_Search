from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

client.delete_collection("codebase")

client.recreate_collection(
    collection_name="codebase",
    vectors_config={
        "size": 3072,   # 🔥 UPDATED
        "distance": "Cosine"
    }
)

print("✅ Qdrant reset with 3072 dimensions")