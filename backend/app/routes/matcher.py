from fastapi import APIRouter, HTTPException
from typing import List
from app.services.preprocess_service import preprocess_text
from app.services.embedding_service import generate_embedding
# 💡 Import the prediction service
from app.services.prediction_service import prediction_service 

router = APIRouter()

# Simple in-memory storage for the current session's data
db = {"jd": None, "resumes": []}

@router.post("/match/")
async def match_resumes():
    """
    Orchestrates the resume matching process by using the prediction service.
    """
    if not db["jd"]:
        raise HTTPException(status_code=404, detail="Job Description not uploaded.")
    if not db["resumes"]:
        raise HTTPException(status_code=404, detail="No resumes uploaded.")

    # 💡 Extract content for batch processing
    resume_contents = [resume["content"] for resume in db["resumes"]]
    jd_content = db["jd"]["content"]
    
    # 💡 Use the efficient predict_batch method to get all scores at once
    predictions = prediction_service.predict_batch(resume_contents, jd_content)

    # 💡 Map the results back to the original resumes
    ranked_resumes = []
    for i, resume in enumerate(db["resumes"]):
        # Use the numerical fit_probability from the prediction service
        score = predictions[i]["fit_probability"] * 100
        # 💡 Include the 'prediction' key from the batch results
        prediction_label = predictions[i]["prediction"] 
        ranked_resumes.append({
            "filename": resume["filename"],
            "score": round(score, 2),
            "prediction": prediction_label
        })

    # Rank the results by score (highest first)
    ranked_resumes.sort(key=lambda x: x["score"], reverse=True)
    
    return {"ranked_resumes": ranked_resumes}

@router.post("/reset/")
async def reset_session():
    """Clears the stored JD and resumes."""
    db["jd"] = None
    db["resumes"] = []
    return {"message": "Session reset."}