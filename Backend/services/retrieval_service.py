from app.services.embedding_service import create_query_embedding
from app.services.faiss_service import get_index, get_chunks, get_metadata, search_query
from app.services.reranker_service import rerank_chunks

def retrieve_relevant_chunks(question: str, k: int = 7):
    index = get_index()
    chunks = get_chunks()
    metadata = get_metadata()

    if index is None or not chunks:
        return []

    query_embedding = create_query_embedding(question)

    retrieved = search_query(
        query_embedding=query_embedding,
        index=index,
        chunks=chunks,
        metadata=metadata,
        k=k
    )

    reranked = rerank_chunks(question, retrieved)

    return reranked[:5]