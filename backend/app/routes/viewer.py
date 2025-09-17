# app/routes/viewer.py

from fastapi import APIRouter
from app.services.view_service import get_resume_file

router = APIRouter()

@router.get("/resumes/{filename}")
async def view_resume(filename: str):
    """
    Handles the API request to view a specific resume file.
    """
    # 💡 CHANGE: Remove the filename argument to prevent forced download
    return get_resume_file(filename)