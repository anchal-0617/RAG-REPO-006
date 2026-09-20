from fastapi import APIRouter
from Backend.models.request_models import QuestionRequest
from Backend.services.query_classifier import classify_query
from Backend.services.retrieval_service import retrieve_relevant_chunks
from Backend.services.answer_service import generate_answer
from Backend.services.summary_service import generate_summary

router = APIRouter()

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        return {"error": "Question cannot be empty"}

    query_type = classify_query(question)

    if query_type == "greeting":
        return {
            "answer": "Hello! Upload your document and ask me anything from it."
        }

    if query_type in ["summary", "analysis"]:
        answer = generate_summary()
        return {"answer": answer}

    retrieved_chunks = retrieve_relevant_chunks(question)

    if not retrieved_chunks:
        return {
            "error": "No document uploaded yet or no relevant content found."
        }

    context = "\n\n".join([item["chunk"] for item in retrieved_chunks])

    answer = generate_answer(question, context)

    return {
        "answer": answer,
        "sources": [
    {
        "filename": item["metadata"]["filename"],
        "chunk_id": item["metadata"]["chunk_id"],
        "source": item["metadata"]["source"],
        "doc_id": item["metadata"]["doc_id"]
    }
    for item in retrieved_chunks
]
        
    }