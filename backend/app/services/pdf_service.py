import os
import shutil

from utils.pdf import extract_text_from_pdf
from utils.chunking import chunk_text
from app.services.embedding_service import create_embedding
from app.services.qdrant_service import store_embedding


def process_pdf(file):

    # Create uploads directory
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Save uploaded file
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    text = extract_text_from_pdf(file_path)

    # Split into chunks
    chunks = chunk_text(text)

    # Create embeddings and store in Qdrant
    for i, chunk in enumerate(chunks):
        embedding = create_embedding(chunk)

        store_embedding(
            chunk,
            embedding,
            file.filename,
            i + 1
        )

    return {
        "message": "File uploaded and stored successfully!",
        "filename": file.filename,
        "chunks": len(chunks)
    }