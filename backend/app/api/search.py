from fastapi import APIRouter

from app.models.schemas import ChatRequest
from app.services.embedding_service import create_embedding
from app.services.llm_service import generate_answer
from app.services.qdrant_service import search_embeddings

router = APIRouter()


@router.post("/search")
def search(request: ChatRequest):

    query_embedding = create_embedding(request.question)

    results = search_embeddings(query_embedding)

    context = ""

    for result in results:
        context += result.payload["text"] + "\n\n"

    answer = generate_answer(
        request.question,
        context
    )

    sources = []

    for result in results:
        sources.append({
            "filename": result.payload["filename"],
            "chunk_number": result.payload["chunk_number"],
            "score": result.score
        })

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources
    }