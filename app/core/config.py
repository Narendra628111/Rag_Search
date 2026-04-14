from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GENERATION_MODEL: str
    EMBEDDING_MODEL: str   # ✅ ADD THIS
    QDRANT_URL: str
    COLLECTION_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()