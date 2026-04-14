from retrieval.retriever import search_code

results = search_code("flask routing")

for r in results:
    print("\n---")
    print("Score:", r["score"])
    print("File:", r["file_path"])
    print(r["code"][:200])