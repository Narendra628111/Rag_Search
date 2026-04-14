
from sentence_transformers import SentenceTransformer

# ✅ Load model ONLY ONCE
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str):
    return model.encode(text).tolist()