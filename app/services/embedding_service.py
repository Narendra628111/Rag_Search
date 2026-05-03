

from typing import List
from sentence_transformers import SentenceTransformer
from app.core.config import settings

# Load once at import time — shared across all calls in the process
_model = SentenceTransformer(settings.EMBEDDING_MODEL)


def get_embedding(text: str) -> List[float]:
    """
    Embed a single string into a 384-dim vector.
    Used by vector_service for BOTH ingestion and search.
    """
    if not text or not text.strip():
        raise ValueError("get_embedding() received empty text.")
    return _model.encode(text).tolist()


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Embed multiple strings in one batched call — much faster than
    calling get_embedding() in a loop during ingest.
    """
    texts = [t for t in texts if t and t.strip()]
    if not texts:
        return []
    return _model.encode(texts, batch_size=64, show_progress_bar=True).tolist()