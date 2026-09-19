import faiss
import numpy as np

stored_chunks = []
stored_metadata = []
faiss_index = None

def create_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def store_chunks(chunks, metadata):
    global stored_chunks, stored_metadata
    stored_chunks = chunks
    stored_metadata = metadata
    print("STORE CHUNKS =", len(stored_chunks))
    print("SOURCES =", set(item["source"] for item in stored_metadata))

def store_index(index):
    global faiss_index
    faiss_index = index
    print("STORE INDEX =", faiss_index)

def get_chunks():
    return stored_chunks

def get_metadata():
    return stored_metadata

def get_index():
    return faiss_index

def search_query(query_embedding, index, chunks, metadata, k=5):
    if index is None:
        return []

    k = min(k, len(chunks))

    D, I = index.search(query_embedding, k)

    results = []

    for idx in I[0]:
        if 0 <= idx < len(chunks):
            results.append({
                "chunk": chunks[idx],
                "metadata": metadata[idx]
            })

    return results