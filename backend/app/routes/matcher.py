from fastapi import APIRouter,HTTPException

from app.services.preprocess_service import preprocess_text
from app.services.embedding_service import generate_embedding
from app.services.scoring_service import calculate_similarity

router = APIRouter()

# Simple in-memory storage for the current session's data
db = {"jd" : None , "resumes" : []}

@router.post("/match/")

async def match_resumes():
    """
    Orchestrates the resume matching process by using all services.
    """

    if not db["jd"]:
        raise HTTPException(status_code = 404 , detail = "Job Description not uploaded.")
    if not db["resumes"]:
        raise HTTPException(status_code = 404 , detail = "No resumes uploaded.")
    
    # Process the Job Description
    processed_jd = preprocess_text(db["jd"]["content"])
    # print("--- PROCESSED JOB DESCRIPTION ---", processed_jd, "\n")
    jd_embedding = generate_embedding(processed_jd)

    # Process and score each resume
    results = []
    for resume in db["resumes"]:
        processed_resume = preprocess_text(resume["content"])
        # print(f"--- PROCESSED RESUME: {resume['filename']} ---", processed_resume, "\n")
        resume_embedding = generate_embedding(processed_resume)

        score = calculate_similarity(jd_embedding, resume_embedding)

        results.append({
            "filename" : resume["filename"],
            "score" : round(score * 100,2)
        })

     # Rank the results by score (highest first)
    ranked_resumes = sorted(results,key = lambda x : x["score"] , reverse = True)
    return {"ranked_resumes" : ranked_resumes}

@router.post("/reset/")
async def reset_session():
    """Clears the stored JD and resumes."""
    db["jd"] = None
    db["resumes"] = []
    return {"message": "Session reset."}