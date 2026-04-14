from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_embedding(text: str):
    # ✅ Fix: avoid empty input
    if not text or not text.strip():
        return None

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return response.embeddings[0].values