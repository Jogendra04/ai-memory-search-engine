from qdrant_client import QdrantClient  # type: ignore[import]
from qdrant_client.models import Distance, VectorParams, PointStruct  # type: ignore[import]
import uuid

# Connect to Qdrant running in Docker
client = QdrantClient(
    url="http://localhost:6333"
)


# Qdrant collection name
COLLECTION_NAME = "memory_documents"


# Create collection if it doesn't exist
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

        print(f"Collection '{COLLECTION_NAME}' created!")

    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")


# Store an embedding in Qdrant
def store_embedding(
    text,
    embedding,
    filename,
    chunk_number,
    file_hash
):

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": text,
                    "filename": filename,
                    "chunk_number": chunk_number,
                    "file_hash": file_hash
                }
            )
        ]
    )

    print(f"Stored chunk {chunk_number} from {filename}")


# Store a memory
def store_memory(title, content, embedding, tags=None):

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
                    "title": title,
                    "content": content,
                    "tags": tags
                }
            )
        ]
    )

    print(f"Stored memory: {title}")


# Search embeddings
def search_embeddings(query_embedding, limit=5):

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit
    )

    return results.points


# Get all memories/documents
def get_all_memories():

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    return results[0]


# Delete memory
def delete_memory(memory_id):

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[memory_id]
    )

    print(f"Deleted memory: {memory_id}")


# Get uploaded documents
def get_documents():

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    points = results[0]

    documents = {}

    for point in points:

        payload = point.payload

        if payload.get("type") == "memory":
            continue

        filename = payload.get("filename")

        if not filename:
            continue

        if filename not in documents:
            documents[filename] = 0

        documents[filename] += 1

    document_list = []

    for filename, chunks in documents.items():

        document_list.append(
            {
                "filename": filename,
                "chunks": chunks
            }
        )

    return document_list


# Delete document
def delete_document(filename):

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    points = results[0]

    ids_to_delete = []

    for point in points:

        payload = point.payload

        if payload.get("filename") == filename:
            ids_to_delete.append(point.id)

    if ids_to_delete:

        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=ids_to_delete
        )

        print(f"Deleted {len(ids_to_delete)} chunks from {filename}")

    return len(ids_to_delete)


# Check if document already exists
def document_exists(file_hash):

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    points = results[0]

    for point in points:
        payload = point.payload

        if payload.get("file_hash") == file_hash:
            return True

    return False