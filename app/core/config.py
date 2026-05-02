from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── LLM (Gemini) — used by llm_service.py for answer generation only ──
    GEMINI_API_KEY: str
    GENERATION_MODEL: str

    # ── Embedding model — used EXCLUSIVELY by embedding_service.py ─────────
    # Must be a sentence-transformers model name (local, free, no API key).
    # Default: all-MiniLM-L6-v2 → 384 dimensions.
    # If you change this, also update VECTOR_SIZE in vector_service.py
    # and re-ingest all repositories.
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── Vector DB ──────────────────────────────────────────────────────────
    QDRANT_URL: str
    COLLECTION_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()