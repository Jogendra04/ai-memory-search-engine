import os
import shutil
import hashlib

from utils.pdf import extract_text_from_pdf
from utils.chunking import chunk_text

from app.services.embedding_service import create_embedding
from app.services.qdrant_service import (
    store_embedding,
    document_exists
)


def process_pdf(file):

    # Create uploads directory
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Save uploaded file
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Generate SHA-256 hash
    with open(file_path, "rb") as pdf:
        file_hash = hashlib.sha256(pdf.read()).hexdigest()

    # Check duplicate document
    if document_exists(file_hash):
        os.remove(file_path)

        return {
            "message": "This document has already been uploaded.",
            "filename": file.filename,
            "duplicate": True
        }

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
            i + 1,
            file_hash
        )

    return {
        "message": "File uploaded and stored successfully!",
        "filename": file.filename,
        "chunks": len(chunks),
        "duplicate": False
    }