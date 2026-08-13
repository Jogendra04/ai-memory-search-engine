from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)

import os

from app.models.user import User
from app.core.dependencies import get_current_user

from app.services.qdrant_service import (
    get_documents,
    delete_document
)


router = APIRouter()


# ==========================================
# Get Uploaded Documents
# ==========================================

@router.get("/documents")
def list_documents(
    current_user: User = Depends(
        get_current_user
    )
):

    return {
        "documents": get_documents(
            current_user.id
        )
    }


# ==========================================
# Delete Uploaded Document
# ==========================================

@router.delete("/documents/{filename}")
def remove_document(
    filename: str,
    current_user: User = Depends(
        get_current_user
    )
):

    # ======================================
    # Delete Document Chunks From Qdrant
    # ======================================

    deleted_chunks = delete_document(
        filename,
        current_user.id
    )


    # ======================================
    # Delete Physical File
    # ======================================

    file_path = os.path.join(
        "uploads",
        str(current_user.id),
        filename
    )

    if os.path.exists(file_path):

        os.remove(file_path)


    # ======================================
    # Document Not Found
    # ======================================

    if deleted_chunks == 0:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )


    # ======================================
    # Success Response
    # ======================================

    return {
        "message": (
            "Document deleted successfully."
        ),
        "deleted_chunks": deleted_chunks
    }