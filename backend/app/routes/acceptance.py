# app/routes/acceptance.py

from fastapi import APIRouter, HTTPException
from app.services.acceptance_service import move_accepted_resume
from .matcher import db

router = APIRouter()

@router.post("/accept-resume/{filename}")
async def accept_resume(filename: str):
    """
    Handles the API request to accept a resume and calls the service
    to perform the file move.
    """
    try:
        move_accepted_resume(db, filename)
        return {"message": f"Resume '{filename}' has been accepted and moved."}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found.")
    except IOError as e:
        raise HTTPException(status_code=500, detail=str(e))