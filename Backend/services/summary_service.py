from langchain_ollama import OllamaLLM
from app.services.faiss_service import get_chunks

llm = OllamaLLM(model="llama3.2:3b")

def generate_summary() -> str:
    chunks = get_chunks()

    if not chunks:
        return "No document uploaded yet."

    context = "\n\n".join(chunks[:8])

    prompt = f"""
You are a document analysis assistant.

Analyze the uploaded document and give:
1. Short summary
2. Main points
3. Important facts
4. Overall meaning

Document:
{context}

Answer:
"""

    return llm.invoke(prompt)