
from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.embedding_service import get_embedding, get_embeddings_batch

def rerank(query: str, results: list, top_k: int = 5) -> list:
    """
    Takes raw Qdrant search results, reranks them by cosine
    similarity between the query embedding and each chunk embedding,
    and returns the top_k most relevant.
    """
    if not results:
        return results

    # 1 call for the query
    query_vec = np.array(get_embedding(query)).reshape(1, -1)

    # 1 batched call for all chunks instead of N individual calls
    contents = [r.payload["content"] for r in results]
    chunk_vecs = np.array(get_embeddings_batch(contents))

    # score all at once with a single matrix operation
    scores = cosine_similarity(query_vec, chunk_vecs)[0]

    ranked = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
    return [r for _, r in ranked[:top_k]]