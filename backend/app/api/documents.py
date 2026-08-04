from fastapi import APIRouter, HTTPException
import os

from app.services.qdrant_service import (
    get_documents,
    delete_document
)

router = APIRouter()


@router.get("/documents")
def list_documents():
    return {
        "documents": get_documents()
    }


@router.delete("/documents/{filename}")
def remove_document(filename: str):

    deleted_chunks = delete_document(filename)

    file_path = os.path.join("uploads", filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    if deleted_chunks == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "message": "Document deleted successfully.",
        "deleted_chunks": deleted_chunks
    }