import os
import shutil
from fastapi import APIRouter, UploadFile, File
from typing import List
from app.services.textextract_service import extract_text_from_file
from .matcher import db # Import the shared 'db'

router = APIRouter()

@router.post("/upload-resumes/")
async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload one or more resume files, store them on the server,
    extract their text, and save the content for the matching process.
    """
    # Create the temporary directory if it doesn't exist
    if not os.path.exists("./temp_resumes"):
        os.makedirs("./temp_resumes")
    
    # Clear any old resumes from the database and temp folder to start a fresh session
    db["resumes"] = []
    
    for file in files:
        # Save the file to the temporary folder
        file_path = f"./temp_resumes/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract the text content
        # Note: You need to reopen the file since the stream was consumed
        with open(file_path, "rb") as saved_file:
            content = extract_text_from_file(saved_file, file.content_type)

        # Add the resume data to the shared 'db', including the file path
        db["resumes"].append({
            "filename": file.filename,
            "content": content,
            "path": file_path # 💡 We now store the file's path
        })
    
    return {
        "message": f"{len(db['resumes'])} resumes uploaded and processed successfully.",
        "filenames": [r["filename"] for r in db["resumes"]]
    }