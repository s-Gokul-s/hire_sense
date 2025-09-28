import math
from fastapi import APIRouter, HTTPException
from app.routes.matcher import db 
from collections import Counter

router = APIRouter()

def get_analytics_data():
    """
    Calculates key analytics metrics from the ranked resume data:
    - Fit Score Distribution (Histogram)
    - Top Skills Summary (across all resumes)
    - Overall Skill Gap (matched vs missing aggregated)
    """
    # Check 1: Data is uploaded
    if not db.get("jd") or not db.get("resumes") or not db["resumes"]:
        # Using 404 since the resource (calculated analytics) is not yet available/found.
        raise HTTPException(status_code=404, detail="Please upload a JD and at least one resume.")

    # Check 2: Matching has been run (scores are present)
    # The score should be added by the /match/ endpoint.
    if not any("score" in r for r in db["resumes"]):
        # Using 400 Bad Request because the request (to view analytics) is invalid
        # without the required prerequisite data (the scores).
        raise HTTPException(status_code=400, detail="Run the /match/ endpoint before checking analytics. Data is present, but scores are missing.")

    # --- 1. Fit Score Distribution (Histogram) ---
    # Scores are assumed to be 0-100
    scores = [r.get("score", 0) for r in db["resumes"]]
    
    # Define bins: 0-20, 20-40, 40-60, 60-80, 80-100
    # Note: We use 5 bins covering 0% to 100%
    bins = [0, 20, 40, 60, 80, 100]
    histogram_counts = [0] * (len(bins) - 1)
    
    for score in scores:
        # Normalize score to 0-100 range if needed, though assumed already in this range
        score = max(0, min(100, score))
        
        # Calculate which bin the score falls into
        if score == 100:
            # 100 goes into the last bin [80, 100]
            histogram_counts[len(bins) - 2] += 1
        else:
            # Calculate bin index (e.g., score 59.9 -> 2, score 60 -> 3)
            bin_size = 20
            index = math.floor(score / bin_size)
            if index < len(bins) - 1:
                histogram_counts[index] += 1
    
    histogram_data = [
        {"range": f"{bins[i]}-{bins[i+1]}%", "count": histogram_counts[i]}
        for i in range(len(bins) - 1)
    ]
    
    # --- 2. Top Skills Summary (across all resumes) & Overall Skill Gap ---
    all_resume_skills = []
    total_matched = 0
    total_missing = 0

    for resume in db["resumes"]:
        # The skills were populated in the /match/ endpoint
        matched_skills = resume.get("matched_skills", [])
        missing_skills = resume.get("missing_skills", [])
        
        # We only count matched skills for the "Top Skills" chart
        all_resume_skills.extend(matched_skills) 
        
        total_matched += len(matched_skills)
        total_missing += len(missing_skills)
        
    skill_counts = Counter(all_resume_skills)
    
    # Get top 8 skills for the chart
    top_skills = skill_counts.most_common(8)

    # --- 3. Overall Skill Gap (Aggregated) ---
    overall_skill_gap = {
        "matched": total_matched,
        "missing": total_missing
    }

    return {
        "score_distribution": histogram_data,
        "top_skills": [{"skill": s[0], "count": s[1]} for s in top_skills],
        "overall_skill_gap": overall_skill_gap,
        "total_candidates": len(db["resumes"])
    }

@router.get("/analytics", summary="Get data for dashboard visualization")
async def get_analytics():
    """Returns calculated data for score distribution and skill summaries."""
    try:
        return get_analytics_data()
    except HTTPException as e:
        # Re-raise explicit HTTP exceptions (400, 404)
        raise e
    except Exception as e:
        # Catch unexpected calculation errors (500)
        print(f"Analytics calculation error: {e}") 
        raise HTTPException(status_code=500, detail=f"An error occurred during analytics calculation: {str(e)}")
