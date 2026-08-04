from fastapi import APIRouter

from app.models.schemas import ChatRequest
from app.services.embedding_service import create_embedding
from app.services.llm_service import generate_answer
from app.services.qdrant_service import search_embeddings

router = APIRouter()


@router.post("/search")
def search(request: ChatRequest):

    # ======================================
    # Create embedding for the user question
    # ======================================

    query_embedding = create_embedding(request.question)

    # ======================================
    # Search Qdrant
    # ======================================

    results = search_embeddings(query_embedding)

    # ======================================
    # Build context
    # ======================================

    context_parts = []

    for result in results:

        payload = result.payload

        # Memory
        if payload.get("type") == "memory":

            context_parts.append(
                f"""
Memory Title: {payload.get("title", "")}
Memory Content: {payload.get("content", "")}
Tags: {", ".join(payload.get("tags", []))}
"""
            )

        # PDF
        else:

            context_parts.append(
                payload.get("text", "")
            )

    context = "\n\n".join(context_parts)

    # ======================================
    # Generate Answer
    # ======================================

    answer = generate_answer(
        request.question,
        context
    )

    # ======================================
    # Build Sources
    # ======================================

    sources = []

    for result in results:

        payload = result.payload

        if payload.get("type") == "memory":

            sources.append({
                "type": "memory",
                "id": str(result.id),
                "title": payload.get("title"),
                "tags": payload.get("tags", []),
                "score": result.score
            })

        else:

            sources.append({
                "type": "document",
                "id": str(result.id),
                "filename": payload.get("filename"),
                "chunk_number": payload.get("chunk_number"),
                "score": result.score
            })

    # ======================================
    # Response
    # ======================================

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources
    }