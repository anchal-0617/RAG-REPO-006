def create_metadata(chunks, filename, source="local", doc_id=None):
    metadata = []

    for i, chunk in enumerate(chunks):
        metadata.append({
            "filename": filename,
            "chunk_id": i + 1,
            "source": source,
            "doc_id": doc_id,
            "preview": chunk[:120]
        })

    return metadata