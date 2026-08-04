from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_service import process_pdf

router = APIRouter()


@router.post("/upload")
def upload_file(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    return process_pdf(file)