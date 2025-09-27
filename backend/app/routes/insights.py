# app/routes/insights.py

from fastapi import APIRouter, HTTPException
from app.services.insights_service import get_skill_matches
from app.routes.matcher import db # We need the shared 'db' to access the resume content

router = APIRouter()

@router.get("/insights/{filename}")
async def get_insights(filename: str):
    """
    Provides a skills-based breakdown for a specific resume.
    """
    if not db["jd"]:
        raise HTTPException(status_code=404, detail="Job description not found.")
    
    # Find the specific resume in our in-memory database
    resume_found = next((r for r in db["resumes"] if r["filename"] == filename), None)
    
    if not resume_found:
        raise HTTPException(status_code=404, detail=f"Resume '{filename}' not found.")
    
    jd_text = db["jd"]["content"]
    resume_text = resume_found["content"]
    
    skills_data = get_skill_matches(jd_text, resume_text)
    
    return {
        "filename": filename,
        "matched_skills": skills_data["matched_skills"],
        "missing_skills": skills_data["missing_skills"]
    }