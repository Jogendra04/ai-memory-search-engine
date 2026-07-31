from fastapi import APIRouter, UploadFile, File

from app.services.pdf_service import process_pdf

router = APIRouter()


@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    return process_pdf(file)