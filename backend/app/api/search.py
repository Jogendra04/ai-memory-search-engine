from fastapi import APIRouter, Depends

from app.models.schemas import ChatRequest
from app.models.user import User

from app.core.dependencies import get_current_user

from app.services.embedding_service import create_embedding
from app.services.llm_service import generate_answer
from app.services.qdrant_service import search_embeddings


router = APIRouter()


@router.post("/search")
def search(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):

    # ==========================================
    # Create embedding for the user's question
    # ==========================================

    query_embedding = create_embedding(
        request.question
    )

    # ==========================================
    # Search Qdrant ONLY for this user
    # ==========================================

    results = search_embeddings(
        query_embedding=query_embedding,
        user_id=current_user.id,
        limit=5
    )

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
    # Generate answer
    # ==========================================

    answer = generate_answer(
        question=request.question,
        context=context,
        user_id=current_user.id
    )

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
        "question": request.question,
        "answer": answer,
        "sources": sources
    }