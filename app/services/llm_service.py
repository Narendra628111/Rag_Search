# app/services/llm_service.py
#
# Uses the new `google.genai` package (replaces deprecated `google.generativeai`).
# Model name is read from .env via settings.GENERATION_MODEL.

from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_answer(query: str, context: str) -> str:
    prompt = f"""
You are an expert code assistant.

Answer the question based ONLY on the provided context.

### Question:
{query}

### Context:
{context}

### Instructions:
- Give clear explanation
- Reference file names if possible
- If not found, say "Not found in codebase"

### Answer:
"""

    response = client.models.generate_content(
        model=settings.GENERATION_MODEL,
        contents=prompt,
    )
    return response.text