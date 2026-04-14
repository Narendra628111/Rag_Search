from embeddings.embedder import get_embedding
import time

start = time.time()
get_embedding("flask routing")
print("Time:", time.time() - start)