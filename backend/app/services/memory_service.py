from app.services.embedding_service import create_embedding

from app.services.qdrant_service import (
    store_memory,
    get_all_memories,
    delete_memory,
    update_memory,
    search_embeddings
)


# Save Memory

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
    embedding = create_embedding(
        memory_text
    )

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


# List Memories

def list_memories(user_id):

    memories = get_all_memories(
        user_id
    )

    results = []

    for memory in memories:

        payload = memory.payload or {}

        if payload.get("type") == "memory":

            results.append(
                {
                    "id": str(memory.id),
                    "title": payload.get(
                        "title"
                    ),
                    "content": payload.get(
                        "content"
                    ),
                    "tags": payload.get(
                        "tags",
                        []
                    )
                }
            )

    return results


# Remove Memory

def remove_memory(
    memory_id,
    user_id
):

    deleted = delete_memory(
        memory_id,
        user_id
    )

    if not deleted:

        return {
            "message": "Memory not found.",
            "id": memory_id
        }

    return {
        "message": "Memory deleted successfully!",
        "id": memory_id
    }


# Edit Memory

def edit_memory(
    memory_id,
    title,
    content,
    tags,
    user_id
):

    if tags is None:
        tags = []

    # Create new text for embedding
    memory_text = f"{title}\n{content}"

    # Generate a NEW embedding
    embedding = create_embedding(
        memory_text
    )

    # Update existing Qdrant point
    updated = update_memory(
        memory_id=memory_id,
        title=title,
        content=content,
        embedding=embedding,
        user_id=user_id,
        tags=tags
    )

    if not updated:

        return {
            "message": "Memory not found.",
            "id": memory_id
        }

    return {
        "message": "Memory updated successfully!",
        "id": memory_id,
        "title": title,
        "content": content,
        "tags": tags
    }


# Search Memories

def search_memories(
    question,
    user_id,
    limit=5
):

    # Create embedding for the user's question
    query_embedding = create_embedding(
        question
    )

    # Search Qdrant using semantic similarity
    memories = search_embeddings(
        query_embedding=query_embedding,
        user_id=user_id,
        limit=limit
    )

    results = []

    for memory in memories:

        payload = memory.payload or {}

        results.append(
            {
                "id": str(memory.id),
                "type": payload.get(
                    "type"
                ),
                "title": payload.get(
                    "title"
                ),
                "content": payload.get(
                    "content"
                ),
                "filename": payload.get(
                    "filename"
                ),
                "text": payload.get(
                    "text"
                ),
                "chunk_number": payload.get(
                    "chunk_number"
                ),
                "score": memory.score
            }
        )

    return results