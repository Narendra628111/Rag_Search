from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── LLM (Gemini) — used by llm_service.py for answer generation only ──
    GEMINI_API_KEY: str
    GENERATION_MODEL: str

   
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── Vector DB ──────────────────────────────────────────────────────────
    QDRANT_URL: str
    COLLECTION_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()