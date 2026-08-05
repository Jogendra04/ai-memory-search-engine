from app.services.embedding_service import create_embedding
from app.services.qdrant_service import (
    store_memory,
    get_all_memories,
    delete_memory
)


def save_memory(
    title,
    content,
    user_id,
    tags=None
):

    if tags is None:
        tags = []

    # Create text for embedding
    memory_text = f"{title}\n{content}"

    # Create embedding
    embedding = create_embedding(memory_text)

    # Store memory in Qdrant
    store_memory(
        title=title,
        content=content,
        embedding=embedding,
        user_id=user_id,
        tags=tags
    )

    return {
        "message": "Memory saved successfully!",
        "title": title,
        "content": content,
        "tags": tags
    }


def list_memories(user_id):

    memories = get_all_memories(user_id)

    results = []

    for memory in memories:

        payload = memory.payload or {}

        if payload.get("type") == "memory":

            results.append({
                "id": str(memory.id),
                "title": payload.get("title"),
                "content": payload.get("content"),
                "tags": payload.get("tags", [])
            })

    return results


def remove_memory(memory_id, user_id):

    delete_memory(
        memory_id,
        user_id
    )

    return {
        "message": "Memory deleted successfully!",
        "id": memory_id
    }