from fastapi import APIRouter

from app.models.schemas import ChatRequest
from app.services.embedding_service import create_embedding
from app.services.llm_service import generate_answer
from app.services.qdrant_service import search_embeddings


router = APIRouter()


@router.post("/search")
def search(request: ChatRequest):

    # --------------------------------
    # Create embedding for question
    # --------------------------------

    query_embedding = create_embedding(request.question)

    # --------------------------------
    # Search Qdrant
    # --------------------------------

    results = search_embeddings(query_embedding)

    # --------------------------------
    # Build context for LLM
    # --------------------------------

    context_parts = []

    for result in results:

        payload = result.payload

        # Memory
        if payload.get("type") == "memory":

            title = payload.get("title", "Untitled Memory")
            content = payload.get("content", "")

            context_parts.append(
                f"Memory Title: {title}\n"
                f"Memory Content: {content}"
            )

        # PDF/document
        else:

            text = payload.get("text", "")

            context_parts.append(text)

    context = "\n\n".join(context_parts)

    # --------------------------------
    # Generate AI answer
    # --------------------------------

    answer = generate_answer(
        request.question,
        context
    )

    # --------------------------------
    # Build sources
    # --------------------------------

    sources = []

    for result in results:

        payload = result.payload

        # Memory source
        if payload.get("type") == "memory":

            sources.append({
                "type": "memory",
                "title": payload.get("title", "Untitled Memory"),
                "tags": payload.get("tags", []),
                "score": result.score,
                "id": str(result.id)
            })

        # PDF/document source
        else:

            sources.append({
                "type": "document",
                "filename": payload.get("filename", "Unknown"),
                "chunk_number": payload.get("chunk_number"),
                "score": result.score,
                "id": str(result.id)
            })

    # --------------------------------
    # Return response
    # --------------------------------

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources
    }