# app/services/acceptance_service.py

import os
import shutil
from typing import Dict, List

def move_accepted_resume(db: Dict, filename: str) -> None:
    """
    Moves a resume file from the temp folder to a permanent accepted folder
    and updates the in-memory database.
    """
    # Find the resume data in the current session's list
    resume_data = next((r for r in db["resumes"] if r["filename"] == filename), None)
    
    if not resume_data:
        raise FileNotFoundError(f"Resume '{filename}' not found in the current session.")
    
    source_path = resume_data["path"]
    
    # Create the 'accepted' directory if it doesn't exist
    if not os.path.exists("./accepted_resumes"):
        os.makedirs("./accepted_resumes")
    
    destination_path = f"./accepted_resumes/{filename}"
    
    try:
        # Move the file to the permanent folder
        shutil.move(source_path, destination_path)
        
        # Remove the accepted resume from the in-memory db
        db["resumes"] = [r for r in db["resumes"] if r["filename"] != filename]
        
    except Exception as e:
        raise IOError(f"Failed to move file: {e}")