from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3.2:3b")

def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are a smart RAG document assistant.

Rules:
1. Answer only from the uploaded document context.
2. If answer is not available, say: "The answer is not available in the uploaded document."
3. Give clear, useful, structured answer.
4. Do not copy large chunks directly.
5. Explain like a helpful AI assistant.

Document Context:
{context}

User Question:
{question}

Final Answer:
"""

    return llm.invoke(prompt)