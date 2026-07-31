from fastapi import APIRouter

from app.models.schemas import ChatRequest

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest):
    return {
        "answer": f"You asked: {request.question}"
    }