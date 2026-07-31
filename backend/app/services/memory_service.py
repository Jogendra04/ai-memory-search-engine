from app.services.embedding_service import create_embedding
from app.services.qdrant_service import store_embedding


def save_memory(title, content):

    # Combine title and content
    memory_text = f"{title}\n{content}"

    # Create embedding
    embedding = create_embedding(memory_text)

    # Store in Qdrant
    store_embedding(
        memory_text,
        embedding,
        "memory",
        0
    )

    return {
        "message": "Memory saved successfully!",
        "title": title,
        "content": content
    }