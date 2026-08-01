from fastapi import APIRouter

from app.services.qdrant_service import get_documents

router = APIRouter()


@router.get("/documents")
def list_documents():
    return {
        "documents": get_documents()
    }