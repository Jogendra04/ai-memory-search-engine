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
from app.services.query_service import build_search_query
from app.services.retrieval_service import rerank_results
from app.services.chat_history import (
    get_history,
    clear_history
)

router = APIRouter()


# ==========================================
# Filter and diversify search results
# ==========================================

def filter_results(
    results,
    max_chunks_per_document=2
):
    """
    Prevent one document from dominating
    the retrieved context.

    Memories are always kept.
    Documents are limited to a maximum
    number of chunks.
    """

    filtered_results = []

    document_counts = {}

    for result in results:

        payload = result.payload or {}

        # --------------------------------------
        # Saved memories
        # --------------------------------------

        if payload.get("type") == "memory":

            filtered_results.append(result)

            continue

        # --------------------------------------
        # Uploaded documents
        # --------------------------------------

        filename = payload.get(
            "filename",
            "Unknown document"
        )

        current_count = document_counts.get(
            filename,
            0
        )

        if current_count >= max_chunks_per_document:
            continue

        filtered_results.append(result)

        document_counts[filename] = (
            current_count + 1
        )

    return filtered_results


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
    # Build conversation-aware search query
    # ==========================================

    try:

        search_query = build_search_query(
            question=question,
            user_id=current_user.id
        )

        query_embedding = create_embedding(
            search_query
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

        # Retrieve more candidates than we finally use.
        # This gives the diversification step
        # enough results to work with.

        results = search_embeddings(
            query_embedding=query_embedding,
            user_id=current_user.id,
            limit=10
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
    # Diversify search results
    # ==========================================

    results = filter_results(results, max_chunks_per_document=2)

    # ==========================================
    # Re-rank results
    # ==========================================

    results = rerank_results(results=results, question=question, max_results=5)



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

# ==========================================
# Get Chat History
# ==========================================

@router.get("/chat/history")
def get_chat_history(
    current_user: User = Depends(get_current_user)
):

    history = get_history(
        user_id=current_user.id,
        limit=50
    )

    return {
        "history": history
    }

# ==========================================
# Clear Chat History
# ==========================================

@router.delete("/chat/history")
def delete_chat_history(
    current_user: User = Depends(get_current_user)
):

    clear_history(
        user_id=current_user.id
    )

    return {
        "message": "Chat history cleared successfully."
    }