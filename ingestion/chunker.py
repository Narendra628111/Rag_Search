def chunk_code(files, chunk_size=500, overlap=50):
    chunks = []

    for file in files:
        content = file["content"]   # string
        file_path = file["file_path"]

        start = 0
        while start < len(content):
            end = start + chunk_size

            chunk_text = content[start:end]

            chunks.append({
                "file_path": file_path,
                "code": chunk_text
            })

            start += chunk_size - overlap

    return chunks