
import os
import shutil
import hashlib

from utils.document import extract_text
from utils.chunking import chunk_text

from app.services.embedding_service import create_embedding
from app.services.qdrant_service import (
    store_embedding,
    document_exists
)


# ==========================================
# Supported File Types
# ==========================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
    ".csv",
    ".md"
}


# ==========================================
# Process Document
# ==========================================

def process_document(
    file,
    user_id
):

    # ======================================
    # Get File Extension
    # ======================================

    filename = file.filename or ""

    extension = os.path.splitext(
        filename
    )[1].lower()

    # ======================================
    # Validate File Type
    # ======================================

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    # ======================================
    # Create Upload Directory
    # ======================================

    upload_dir = "uploads"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    # ======================================
    # Save Uploaded File
    # ======================================

    file_path = os.path.join(
        upload_dir,
        filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # ======================================
    # Generate SHA-256 Hash
    # ======================================

    with open(
        file_path,
        "rb"
    ) as uploaded_file:

        file_hash = hashlib.sha256(
            uploaded_file.read()
        ).hexdigest()

    # ======================================
    # Check Duplicate Document
    # ======================================

    if document_exists(
        file_hash,
        user_id
    ):

        os.remove(file_path)

        return {
            "message": (
                "This document has "
                "already been uploaded."
            ),
            "filename": filename,
            "duplicate": True
        }

    # ======================================
    # Extract Text
    # ======================================

    try:

        text = extract_text(
            file_path,
            extension
        )

    except Exception as error:

        if os.path.exists(file_path):
            os.remove(file_path)

        raise ValueError(
            f"Unable to extract text: {error}"
        ) from error

    # ======================================
    # Validate Extracted Text
    # ======================================

    if not text.strip():

        if os.path.exists(file_path):
            os.remove(file_path)

        raise ValueError(
            "No readable text was found "
            "in the uploaded file."
        )

    # ======================================
    # Split Into Chunks
    # ======================================

    chunks = chunk_text(text)

    # ======================================
    # Create Embeddings
    # ======================================

    for i, chunk in enumerate(chunks):

        embedding = create_embedding(
            chunk
        )

        store_embedding(
            text=chunk,
            embedding=embedding,
            filename=filename,
            chunk_number=i + 1,
            file_hash=file_hash,
            user_id=user_id
        )

    # ======================================
    # Return Result
    # ======================================

    return {
        "message": (
            "File uploaded and stored "
            "successfully!"
        ),
        "filename": filename,
        "file_type": extension,
        "chunks": len(chunks),
        "duplicate": False
    }