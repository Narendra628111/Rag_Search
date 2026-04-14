from embeddings.embedder import get_embedding
from vector_db.client import client

COLLECTION_NAME = "codebase"

def search_code(query: str, limit=5):
    # Convert query → embedding
    query_vector = get_embedding(query)

    # Search in Qdrant
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )

    output = []
    for res in results:
        output.append({
            "score": res.score,
            "file_path": res.payload["file_path"],
            "code": res.payload["code"]
        })

    return output