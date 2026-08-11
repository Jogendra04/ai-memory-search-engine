
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from app.models.user import User
from app.core.dependencies import get_current_user

from app.services.document_service import (
    process_document
)


router = APIRouter()


# ==========================================
# Supported File Types
# ==========================================

SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}


# ==========================================
# Upload Document
# ==========================================

@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(
        get_current_user
    )
):

    # ======================================
    # Validate File
    # ======================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Please select a file."
        )

    # ======================================
    # Validate Content Type
    # ======================================

    if (
        file.content_type
        not in SUPPORTED_CONTENT_TYPES
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Supported formats: "
                "PDF, TXT, DOCX, CSV, MD."
            )
        )

    # ======================================
    # Process Document
    # ======================================

    try:

        return process_document(
            file=file,
            user_id=current_user.id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:

        print(
            f"Document processing error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to process the "
                "uploaded document."
            )
        ) from error