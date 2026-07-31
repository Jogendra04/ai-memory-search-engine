from fastapi import APIRouter

from app.models.schemas import MemoryRequest
from app.services.memory_service import save_memory


router = APIRouter()


@router.post("/memory")
def create_memory(request: MemoryRequest):

    return save_memory(
        request.title,
        request.content
    )