import os
import uuid

from dotenv import load_dotenv

from qdrant_client import QdrantClient  # type: ignore[import]
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)


# ==========================
# Load Environment Variables
# ==========================

load_dotenv()


# ==========================
# Qdrant Configuration
# ==========================

QDRANT_URL = os.getenv("QDRANT_URL")

if QDRANT_URL is None:
    raise RuntimeError(
        "QDRANT_URL is not configured. "
        "Please add QDRANT_URL to your .env file."
    )


# ==========================
# Connect to Qdrant
# ==========================

client = QdrantClient(
    url=QDRANT_URL
)


COLLECTION_NAME = "memory_documents"


# ==========================
# Create Collection
# ==========================

def create_collection():

    collections = client.get_collections()

    existing_collections = [
        collection.name
        for collection in collections.collections
    ]

    if COLLECTION_NAME not in existing_collections:

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=768,
                distance=Distance.COSINE
            )
        )

        print(
            f"Collection '{COLLECTION_NAME}' created!"
        )

    else:

        print(
            f"Collection '{COLLECTION_NAME}' already exists."
        )


# ==========================
# Store Document Embedding
# ==========================

def store_embedding(
    text,
    embedding,
    filename,
    chunk_number,
    file_hash,
    user_id
):

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "user_id": user_id,
                    "filename": filename,
                    "text": text,
                    "chunk_number": chunk_number,
                    "file_hash": file_hash
                }
            )
        ]
    )

    print(
        f"Stored chunk {chunk_number} from {filename}"
    )


# ==========================
# Store Memory
# ==========================

def store_memory(
    title,
    content,
    embedding,
    user_id,
    tags=None
):

    if tags is None:
        tags = []

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "type": "memory",
                    "user_id": user_id,
                    "title": title,
                    "content": content,
                    "tags": tags
                }
            )
        ]
    )

    print(
        f"Stored memory: {title}"
    )


# ==========================
# Search Embeddings
# ==========================

def search_embeddings(
    query_embedding,
    user_id,
    limit=5
):

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(
                        value=user_id
                    )
                )
            ]
        ),
        limit=limit
    )

    return results.points


# ==========================
# Get All Memories/Documents
# ==========================

def get_all_memories(user_id):

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    points = results[0]

    user_memories = []

    for point in points:

        payload = point.payload or {}

        if payload.get("user_id") != user_id:
            continue

        user_memories.append(point)

    return user_memories


# ==========================
# Delete Memory
# ==========================

def delete_memory(
    memory_id,
    user_id
):

    # Make sure the memory belongs to
    # the current user before deleting.

    results = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[memory_id],
        with_payload=True,
        with_vectors=False
    )

    if not results:
        return False

    payload = results[0].payload or {}

    if payload.get("user_id") != user_id:
        return False

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[memory_id]
    )

    print(
        f"Deleted memory: {memory_id}"
    )

    return True


# ==========================
# Get Uploaded Documents
# ==========================

def get_documents(user_id):

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    points = results[0]

    documents = {}

    for point in points:

        payload = point.payload or {}

        if payload.get("user_id") != user_id:
            continue

        if payload.get("type") == "memory":
            continue

        filename = payload.get("filename")

        if not filename:
            continue

        documents[filename] = (
            documents.get(filename, 0) + 1
        )

    return [
        {
            "filename": filename,
            "chunks": chunks
        }
        for filename, chunks in documents.items()
    ]


# ==========================
# Delete Document
# ==========================

def delete_document(
    filename,
    user_id
):

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    points = results[0]

    ids_to_delete = []

    for point in points:

        payload = point.payload or {}

        if (
            payload.get("filename") == filename
            and payload.get("user_id") == user_id
        ):
            ids_to_delete.append(point.id)

    if ids_to_delete:

        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=ids_to_delete
        )

        print(
            f"Deleted {len(ids_to_delete)} "
            f"chunks from {filename}"
        )

    return len(ids_to_delete)


# ==========================
# Check If Document Exists
# ==========================

def document_exists(
    file_hash,
    user_id
):

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    points = results[0]

    for point in points:

        payload = point.payload or {}

        if (
            payload.get("file_hash") == file_hash
            and payload.get("user_id") == user_id
        ):
            return True

    return False