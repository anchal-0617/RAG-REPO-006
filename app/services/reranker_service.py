def rerank_chunks(question: str, retrieved_chunks):
    question_words = set(question.lower().split())

    scored_chunks = []

    for item in retrieved_chunks:
        chunk = item["chunk"]
        chunk_words = set(chunk.lower().split())

        score = len(question_words.intersection(chunk_words))

        scored_chunks.append({
            "chunk": chunk,
            "metadata": item["metadata"],
            "score": score
        })

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)

    return scored_chunks