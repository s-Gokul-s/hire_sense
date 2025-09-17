# app/services/view_service.py

import os
from fastapi import HTTPException
# 💡 NEW: Import StreamingResponse and a standard file library
from fastapi.responses import StreamingResponse
import io

def get_resume_file(filename: str, folder: str = "./temp_resumes"):
    """
    Retrieves a resume file from a specified folder for inline viewing.
    """
    file_path = os.path.join(folder, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    try:
        # Open the file in binary read mode
        with open(file_path, "rb") as file_handle:
            # 💡 NEW: Read the file content into an in-memory buffer
            file_content = io.BytesIO(file_handle.read())
        
        # 💡 NEW: Return a StreamingResponse with the correct headers for inline viewing
        return StreamingResponse(
            file_content,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")