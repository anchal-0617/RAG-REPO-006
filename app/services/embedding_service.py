from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(texts):
    embeddings = model.encode(texts)
    return np.array(embeddings).astype("float32")

def create_query_embedding(question: str):
    embedding = model.encode([question])
    return np.array(embedding).astype("float32")