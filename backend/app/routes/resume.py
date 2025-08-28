# resume.py (Updated)

from fastapi import APIRouter, UploadFile, File
from typing import List
# --- CHANGE 1: Import the unified extractor for more flexibility ---
from app.services.textextract_service import extract_text_from_file
# --- CHANGE 2: Import the shared 'db' from the matcher route ---
from .matcher import db

router = APIRouter()

@router.post("/upload-resumes/")
async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload one or more resume files (PDF, DOCX, TXT),
    extract their text, and store it for the matching process.
    """
    # --- CHANGE 3: Clear any old resumes to start a fresh session ---
    db["resumes"] = [] 
    
    for file in files:
        # Use the unified extractor to handle different file types
        content = extract_text_from_file(file.file, file.content_type)
        
        # --- CHANGE 4: Add the extracted resume data to the shared 'db' ---
        db["resumes"].append({
            "filename": file.filename,
            "content": content
        })
        
    # --- CHANGE 5: Return a clear success message ---
    return {
        "message": f"{len(db['resumes'])} resumes uploaded and processed successfully.",
        "filenames": [r["filename"] for r in db["resumes"]]
    }