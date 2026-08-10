
from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import ChatRequest
from app.models.user import User

from app.core.dependencies import get_current_user

from app.services.embedding_service import create_embedding
from app.services.llm_service import generate_answer
from app.services.qdrant_service import (
    search_embeddings,
    QdrantServiceError
)


router = APIRouter()


@router.post("/search")
def search(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):

    # ==========================================
    # Validate question
    # ==========================================

    question = request.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    # ==========================================
    # Create embedding for the user's question
    # ==========================================

    try:

        query_embedding = create_embedding(
            question
        )

    except Exception as error:

        print(
            f"Embedding error: {error}"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to process your question. "
                "Please try again."
            )
        ) from error

    # ==========================================
    # Search Qdrant ONLY for this user
    # ==========================================

    try:

        results = search_embeddings(
            query_embedding=query_embedding,
            user_id=current_user.id,
            limit=5
        )

    except QdrantServiceError as error:

        print(
            f"Search database error: {error}"
        )

        raise HTTPException(
            status_code=503,
            detail=str(error)
        ) from error

    # ==========================================
    # Build context
    # ==========================================

    context_parts = []

    for result in results:

        payload = result.payload or {}

        # --------------------------------------
        # Saved memory
        # --------------------------------------

        if payload.get("type") == "memory":

            title = payload.get(
                "title",
                ""
            )

            content = payload.get(
                "content",
                ""
            )

            tags = payload.get(
                "tags",
                []
            )

            context_parts.append(
                f"""
SOURCE TYPE: SAVED MEMORY

Memory Title:
{title}

Memory Content:
{content}

Tags:
{", ".join(tags)}
"""
            )

        # --------------------------------------
        # Uploaded document
        # --------------------------------------

        else:

            filename = payload.get(
                "filename",
                "Unknown document"
            )

            chunk_number = payload.get(
                "chunk_number",
                ""
            )

            text = payload.get(
                "text",
                ""
            )

            context_parts.append(
                f"""
SOURCE TYPE: UPLOADED DOCUMENT

Filename:
{filename}

Chunk:
{chunk_number}

Content:
{text}
"""
            )

    context = "\n\n".join(
        context_parts
    )

    # ==========================================
    # Generate answer using Llama
    # ==========================================

    try:

        answer = generate_answer(
            question=question,
            context=context,
            user_id=current_user.id
        )

    except Exception as error:

        print(
            f"LLM error: {error}"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service is currently "
                "unavailable. Please try again."
            )
        ) from error

    # ==========================================
    # Build sources
    # ==========================================

    sources = []

    for result in results:

        payload = result.payload or {}

        # --------------------------------------
        # Memory source
        # --------------------------------------

        if payload.get("type") == "memory":

            sources.append(
                {
                    "type": "memory",
                    "id": str(result.id),
                    "title": payload.get(
                        "title"
                    ),
                    "tags": payload.get(
                        "tags",
                        []
                    ),
                    "score": result.score
                }
            )

        # --------------------------------------
        # Document source
        # --------------------------------------

        else:

            sources.append(
                {
                    "type": "document",
                    "id": str(result.id),
                    "filename": payload.get(
                        "filename"
                    ),
                    "chunk_number": payload.get(
                        "chunk_number"
                    ),
                    "score": result.score
                }
            )

    # ==========================================
    # Return response
    # ==========================================

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }