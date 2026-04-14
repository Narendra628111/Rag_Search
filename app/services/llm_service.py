import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel(settings.GENERATION_MODEL)

def generate_answer(query: str, context: str):
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

    response = model.generate_content(prompt)
    return response.text