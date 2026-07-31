from app.services.embedding_service import create_embedding
from app.services.qdrant_service import (
    store_memory,
    get_all_memories,
    delete_memory
)


def save_memory(title, content, tags=None):

    if tags is None:
        tags = []

    # Create text that will be converted into an embedding
    memory_text = f"{title}\n{content}"

    # Create embedding
    embedding = create_embedding(memory_text)

    # Store memory in Qdrant
    store_memory(
        title=title,
        content=content,
        embedding=embedding,
        tags=tags
    )

    return {
        "message": "Memory saved successfully!",
        "title": title,
        "content": content,
        "tags": tags
    }


def list_memories():

    memories = get_all_memories()

    results = []

    for memory in memories:

        payload = memory.payload

        # Only return actual memories
        if payload.get("type") == "memory":

            results.append({
                "id": str(memory.id),
                "title": payload.get("title"),
                "content": payload.get("content"),
                "tags": payload.get("tags", [])
            })

    return results

def remove_memory(memory_id):

    delete_memory(memory_id)

    return {
        "message": "Memory deleted successfully!",
        "id": memory_id
    }