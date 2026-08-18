from fastapi import APIRouter, Depends

from app.models.schemas import ChatRequest
from app.models.user import User

from app.core.dependencies import get_current_user

from app.services.chat_history import (
    get_history,
    clear_history
)

router = APIRouter()

# Old Chat Test Endpoint

@router.post("/chat")
def chat(
    request: ChatRequest
):

    return {
        "answer": f"You asked: {request.question}"
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