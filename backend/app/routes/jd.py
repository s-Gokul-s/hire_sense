#  FastAPI Route to Upload and Extract Text from Job Description

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.textextract_service import extract_text_from_file
import os


router = APIRouter()

@router.post("/upload-jd")

async def upload_jd(
    jd_text: Optional[str] = Form(None),
    jd_upload: Optional[UploadFile] = File(None)  
):
    """
    Accept JD as plain text or upload a PDF/DOCX/TXT file.
    Returns extracted content.
    """
    if jd_text:
        return{
            "source":"text",
            "content": jd_text.strip()
        }
    elif jd_upload and isinstance(jd_upload, UploadFile):
        try:
            file_type = os.path.splitext(jd_upload.filename)[1].lower().replace('.', '')
            content =  extract_text_from_file(jd_upload.file,jd_upload.content_type)
            return {
                "source":file_type,
                "filename":jd_upload.filename,
                "content": content
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error extracting text from file ")
    else:
            raise HTTPException(status_code=400, detail="Either JD text or JD file must be provided.")


        