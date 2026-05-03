# app/services/llm_service.py
#
# Uses the new `google.genai` package (replaces deprecated `google.generativeai`).
# Model name is read from .env via settings.GENERATION_MODEL.

from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_answer(query: str, context: str) -> str:
    prompt = f"""
You are an expert code assistant helping developers understand and modify a codebase.

### Question:
{query}

### Relevant code from the codebase:
{context}

### Instructions:
- Use the context to understand the current code structure
- If the question asks how to ADD or MODIFY something, suggest the exact code changes based on what you see
- Reference actual file names, class names, and variable names from the context
- Be specific and practical — show code examples
- Only say "Not found in codebase" if the context is completely empty

### Answer:
"""

    response = client.models.generate_content(
        model=settings.GENERATION_MODEL,
        contents=prompt,
    )
    return response.text