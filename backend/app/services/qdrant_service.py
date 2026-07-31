from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
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
def store_embedding(text, embedding, filename, chunk_number):

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": text,
                    "filename": filename,
                    "chunk_number": chunk_number
                }
            )
        ]
    )

    print(f"Stored chunk {chunk_number} from {filename}")

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

# Search for similar embeddings
def search_embeddings(query_embedding, limit=5):

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit
    )

    return results.points


# Get all stored memories/documents
def get_all_memories():

    results = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    return results[0]

def delete_memory(memory_id):

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[memory_id]
    )

    print(f"Deleted memory: {memory_id}")