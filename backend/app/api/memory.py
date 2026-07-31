from fastapi import APIRouter

from app.models.schemas import MemoryRequest
from app.services.memory_service import (
    save_memory,
    list_memories,
    remove_memory
)


router = APIRouter()


@router.post("/memory")
def create_memory(request: MemoryRequest):

    return save_memory(
        title=request.title,
        content=request.content,
        tags=request.tags
    )


@router.get("/memories")
def get_memories():

    return {
        "memories": list_memories()
    }

@router.delete("/memory/{memory_id}")
def delete_memory_endpoint(memory_id: str):

    return remove_memory(memory_id)