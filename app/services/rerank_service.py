# app/services/rerank_service.py
from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.vector_service import get_embedding   # single source of truth

def rerank(query: str, results: list, top_k: int = 5) -> list:
    """
    Takes raw Qdrant search results (top-10), reranks them by cosine
    similarity between the query embedding and each chunk embedding,
    and returns the top_k most relevant.
    """
    if not results:
        return results

    query_vec = np.array(get_embedding(query)).reshape(1, -1)

    scored = []
    for r in results:
        chunk_vec = np.array(get_embedding(r.payload["content"])).reshape(1, -1)
        score = cosine_similarity(query_vec, chunk_vec)[0][0]
        scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:top_k]]