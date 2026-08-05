from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.pdf_service import process_pdf


router = APIRouter()


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    print(f"User ID: {current_user.id}")
    print(f"User Email: {current_user.email}")

    return process_pdf(
    file=file,
    user_id=current_user.id
    )