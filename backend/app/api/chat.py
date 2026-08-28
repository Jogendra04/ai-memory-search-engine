from fastapi import APIRouter, Depends

from app.models.schemas import ChatRequest
from app.models.user import User

from app.core.dependencies import get_current_user

from app.services.chat_history import (
    get_history,
    clear_history
)

from app.services.llm_service import generate_answer
from app.services.memory_service import search_memories


router = APIRouter()


# Chat with AI

@router.post("/chat")
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):

    # Search relevant memories/documents
    results = search_memories(
        query=request.question,
        user_id=current_user.id
    )

    # Build context from retrieved memories
    context_parts = []

    for result in results:

        content = result.get("content")

        if content:
            context_parts.append(content)

    context = "\n\n".join(context_parts)

    # Generate answer using Gemini
    answer = generate_answer(
        question=request.question,
        context=context,
        user_id=current_user.id,
        sources=results
    )

    return {
        "answer": answer,
        "sources": results
    }


# Get Chat History

@router.get("/chat/history")
def get_chat_history(
    current_user: User = Depends(
        get_current_user
    )
):

    history = get_history(
        user_id=current_user.id,
        limit=50
    )

    return {
        "history": history
    }


# Clear Chat History

@router.delete("/chat/history")
def delete_chat_history(
    current_user: User = Depends(
        get_current_user
    )
):

    clear_history(
        user_id=current_user.id
    )

    return {
        "message": "Chat history cleared successfully."
    }