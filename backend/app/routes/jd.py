# jd.py (Updated)

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.textextract_service import extract_text_from_file
import os

# Import the shared 'db' from the matcher route
from .matcher import db 

router = APIRouter()

@router.post("/upload-jd")
async def upload_jd(
    jd_text: Optional[str] = Form(None),
    jd_upload: Optional[UploadFile] = File(None)
):
    """
    Accept JD as plain text or upload a PDF/DOCX/TXT file,
    then store the content for the matching process.
    """
    content = ""
    filename = "text_input" # A default name for text input

    if not jd_text and not jd_upload:
        raise HTTPException(status_code=400, detail="Either JD text or JD file must be provided.")

    if jd_upload:
        try:
            content = extract_text_from_file(jd_upload.file, jd_upload.content_type)
            filename = jd_upload.filename
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    # Use 'elif' since we prioritize the file upload
    elif jd_text:
        content = jd_text.strip()

    # --- KEY ADDITION ---
    # Store the extracted content and filename in the shared 'db' dictionary.
    db["jd"] = {"filename": filename, "content": content}
    
    # Return a success message confirming the action.
    return {
        "message": "Job Description uploaded and processed successfully.",
        "jd_details": db["jd"]
    }