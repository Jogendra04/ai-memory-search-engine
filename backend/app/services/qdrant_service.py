import os
import uuid

from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)


# Load Environment Variables

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL:
    raise RuntimeError("QDRANT_URL is not configured.")

if not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_API_KEY is not configured.")


# Qdrant Client

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

COLLECTION_NAME = "memory_documents"


# Custom Qdrant Error

class QdrantServiceError(Exception):
    """
    Raised when the Qdrant service is unavailable
    or an operation fails.
    """
    pass


# Create Collection and Payload Index

def create_collection():

    try:

        collections = client.get_collections()

        existing_collections = [
            collection.name
            for collection in collections.collections
        ]

        # Create collection if it does not exist

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

        # Create user_id payload index

        try:

            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="user_id",
                field_schema=PayloadSchemaType.KEYWORD
            )

            print(
                "Payload index for 'user_id' created or already exists."
            )

        except Exception as error:

            # Qdrant may return an error if the index
            # already exists. We don't want this to
            # stop the application.

            error_message = str(error).lower()

            if (
                "already exists" in error_message
                or "duplicate" in error_message
            ):

                print(
                    "Payload index for 'user_id' already exists."
                )

            else:

                print(
                    f"Payload index warning: {error}"
                )

    except Exception as error:

        print(
            f"Qdrant collection error: {error}"
        )

        raise QdrantServiceError(
            "Unable to connect to the search database."
        ) from error


# Scroll All Points

def scroll_all_points():

    all_points = []

    offset = None

    try:

        while True:

            results, next_offset = client.scroll(
                collection_name=COLLECTION_NAME,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            all_points.extend(results)

            if next_offset is None:
                break

            offset = next_offset

        return all_points

    except Exception as error:

        print(
            f"Qdrant pagination error: {error}"
        )

        raise QdrantServiceError(
            "Unable to retrieve data from the search database."
        ) from error


# Store Document Embedding

def store_embedding(
    text,
    embedding,
    filename,
    chunk_number,
    file_hash,
    user_id
):

    try:

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "type": "document",
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

    except Exception as error:

        print(
            f"Qdrant document storage error: {error}"
        )

        raise QdrantServiceError(
            "Unable to store the document in the search database."
        ) from error


# Store Memory

def store_memory(
    title,
    content,
    embedding,
    user_id,
    tags=None
):

    if tags is None:
        tags = []

    try:

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

    except Exception as error:

        print(
            f"Qdrant memory storage error: {error}"
        )

        raise QdrantServiceError(
            "Unable to save the memory in the search database."
        ) from error


# Update Memory

def update_memory(
    memory_id,
    title,
    content,
    embedding,
    user_id,
    tags=None
):

    if tags is None:
        tags = []

    try:

        # Get the existing memory

        results = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[memory_id],
            with_payload=True,
            with_vectors=False
        )

        # Memory does not exist

        if not results:
            return False

        existing_payload = results[0].payload or {}

        # Make sure the memory belongs to this user

        if existing_payload.get("user_id") != user_id:
            return False

        # Update existing Qdrant point

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=memory_id,
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
            f"Updated memory: {memory_id}"
        )

        return True

    except Exception as error:

        print(
            f"Qdrant memory update error: {error}"
        )

        raise QdrantServiceError(
            "Unable to update the memory."
        ) from error


# Search Embeddings

def search_embeddings(
    query_embedding,
    user_id,
    limit=5
):

    try:

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

    except Exception as error:

        print(
            f"Qdrant search error: {error}"
        )

        raise QdrantServiceError(
            "Unable to search your documents and memories."
        ) from error


# Get All Memories/Documents

def get_all_memories(user_id):

    try:

        points = scroll_all_points()

        user_memories = []

        for point in points:

            payload = point.payload or {}

            if payload.get("user_id") != user_id:
                continue

            user_memories.append(point)

        return user_memories

    except Exception as error:

        print(
            f"Qdrant memory retrieval error: {error}"
        )

        raise QdrantServiceError(
            "Unable to load your memories."
        ) from error


# Delete Memory

def delete_memory(
    memory_id,
    user_id
):

    try:

        # Get memory

        results = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[memory_id],
            with_payload=True,
            with_vectors=False
        )

        if not results:
            return False

        payload = results[0].payload or {}

        # Make sure memory belongs to current user

        if payload.get("user_id") != user_id:
            return False

        # Delete memory

        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[memory_id]
        )

        print(
            f"Deleted memory: {memory_id}"
        )

        return True

    except Exception as error:

        print(
            f"Qdrant memory deletion error: {error}"
        )

        raise QdrantServiceError(
            "Unable to delete the memory."
        ) from error


# Get Uploaded Documents

def get_documents(user_id):

    try:

        points = scroll_all_points()

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

    except Exception as error:

        print(
            f"Qdrant document retrieval error: {error}"
        )

        raise QdrantServiceError(
            "Unable to load your documents."
        ) from error


# Delete Document

def delete_document(
    filename,
    user_id
):

    try:

        points = scroll_all_points()

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

    except Exception as error:

        print(
            f"Qdrant document deletion error: {error}"
        )

        raise QdrantServiceError(
            "Unable to delete the document."
        ) from error


# Check If Document Exists

def document_exists(
    file_hash,
    user_id
):

    try:

        points = scroll_all_points()

        for point in points:

            payload = point.payload or {}

            if (
                payload.get("file_hash") == file_hash
                and payload.get("user_id") == user_id
            ):

                return True

        return False

    except Exception as error:

        print(
            f"Qdrant document check error: {error}"
        )

        raise QdrantServiceError(
            "Unable to check the document."
        ) from error