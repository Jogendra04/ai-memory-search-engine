from fastapi import APIRouter, Depends

from app.models.schemas import MemoryRequest
from app.models.user import User

from app.core.dependencies import get_current_user

from app.services.memory_service import (
    save_memory,
    list_memories,
    remove_memory,
    edit_memory
)

router = APIRouter()


@router.post("/memory")
def create_memory(
    request: MemoryRequest,
    current_user: User = Depends(
        get_current_user
    )
):

    return save_memory(
        title=request.title,
        content=request.content,
        tags=request.tags,
        user_id=current_user.id
    )


@router.get("/memories")
def get_memories(
    current_user: User = Depends(
        get_current_user
    )
):

    return {
        "memories": list_memories(
            current_user.id
        )
    }


@router.put("/memory/{memory_id}")
def update_memory_endpoint(
    memory_id: str,
    request: MemoryRequest,
    current_user: User = Depends(
        get_current_user
    )
):

    return edit_memory(
        memory_id=memory_id,
        title=request.title,
        content=request.content,
        tags=request.tags,
        user_id=current_user.id
    )


@router.delete("/memory/{memory_id}")
def delete_memory_endpoint(
    memory_id: str,
    current_user: User = Depends(
        get_current_user
    )
):

    return remove_memory(
        memory_id,
        current_user.id
    )