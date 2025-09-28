import io
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse

# IMPORTANT: Ensure these imports are correct based on your project structure.
# We need access to the data store (db) and the scoring/insights functions.
from app.routes.matcher import db # Assuming 'db' (data store) is defined/imported in app.routes.matcher
from app.services.prediction_service import prediction_service as scoring_service 
from app.services.insights_service import get_skill_matches 

# Import the reporting service functions you just defined
from app.services.report_service import generate_excel_report, generate_csv_report, generate_resumes_zip

router = APIRouter()

def _prepare_ranked_data() -> List[Dict[str, Any]] | None:
    """
    Calculates scores, extracts skills, and ranks the resumes currently in db["resumes"].
    Returns None if essential data is missing.
    """
    # Use .get() for safer access in case keys are missing
    if not db.get("jd") or not db.get("resumes"):
        return None

    jd_text = db["jd"]["content"]
    report_data = []
    
    # 1. Gather data and calculate scores/insights
    for resume in db["resumes"]:
        resume_text = resume["content"]
        
        # Re-run prediction and insights to ensure up-to-date data for the report
        prediction_result = scoring_service.predict(resume_text, jd_text)
        skills_data = get_skill_matches(jd_text, resume_text)
        
        # --- KEY FIX ---
        # The prediction service returns a string like "85.50%". We must convert it to a number.
        hybrid_score_str = prediction_result["hybrid_fit_score"]
        # Strip the '%' sign and convert the result to a float for calculation.
        relevance_score = float(hybrid_score_str.strip('%')) 
        
        # We store the float value for sorting and the formatted string for display.
        report_data.append({
            "Resume Filename": resume["filename"],
            # Store the score as an integer percentage for sorting and Excel
            "Relevance Score (%)": int(round(relevance_score)),
            "Matched Skills": ", ".join(skills_data["matched_skills"]),
            "Missing Skills": ", ".join(skills_data["missing_skills"]),
        })

    # 2. Sort by score
    sorted_data = sorted(report_data, key=lambda x: x["Relevance Score (%)"], reverse=True)

    # 3. Add rank
    for i, item in enumerate(sorted_data):
        item["Rank"] = i + 1

    return sorted_data

@router.get("/reports/export-excel", summary="Export Ranked Resumes & Skills to Excel")
async def export_excel_report(limit: Optional[int] = Query(None, description="Limit the number of resumes to export")):
    """Delegates to the service layer to generate and stream an Excel file."""
    ranked_data = _prepare_ranked_data()
    if ranked_data is None:
        raise HTTPException(status_code=404, detail="No job description or resumes have been uploaded.")
    
    # Apply limit
    if limit is not None and limit > 0:
        ranked_data = ranked_data[:limit]

    excel_buffer = generate_excel_report(ranked_data)
    
    return StreamingResponse(
        content=excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=resume_insights.xlsx"}
    )


@router.get("/reports/download-resumes-zip", summary="Download all remaining ranked resumes as a ZIP file")
async def download_remaining_resumes(limit: Optional[int] = Query(None, description="Limit the number of resumes to download")):
    """
    Creates a ZIP archive containing the top N resume files based on the ranked list (db['resumes']).
    """
    if not db.get("resumes"):
        raise HTTPException(status_code=404, detail="No resumes remain in the current ranked list to download.")
    
    # Sort the resumes by score before applying the limit
    # This assumes a 'score' key is added by a /match endpoint.
    sorted_resumes = sorted(db["resumes"], key=lambda r: r.get("score", 0), reverse=True)
    
    # Apply the limit to the sorted list
    resumes_to_zip = sorted_resumes[:limit] if limit is not None and limit > 0 else sorted_resumes

    if not resumes_to_zip:
        raise HTTPException(status_code=404, detail="No resumes found for the specified limit.")

    # Pass the correctly filtered list of resume dictionaries to the service function
    zip_buffer = generate_resumes_zip(resumes_to_zip)

    return StreamingResponse(
        content=zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=ranked_resumes.zip"}
    )