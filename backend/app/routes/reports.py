import io
from typing import List, Dict, Any
from fastapi import APIRouter
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
        
        hybrid_score_str = prediction_result["hybrid_fit_score"]
        # Convert "85.50%" -> 85.5 for proper numerical sorting
        relevance_score = float(hybrid_score_str.strip('%')) 
        
        report_data.append({
            "Resume Filename": resume["filename"],
            "Relevance Score (Float)": relevance_score, # Use float for internal sorting
            "Matched Skills": ", ".join(skills_data["matched_skills"]),
            "Missing Skills": ", ".join(skills_data["missing_skills"])
        })

    # 2. Sort data by relevance score
    ranked_data = sorted(report_data, key=lambda x: x["Relevance Score (Float)"], reverse=True)

    # 3. Add Rank column and format score back to percentage string for display
    final_ranked_data = []
    for i, data in enumerate(ranked_data):
        # Remove the float score key and add display score
        score_float = data.pop("Relevance Score (Float)")
        
        final_ranked_data.append({
            "Rank": i + 1,
            "Resume Filename": data["Resume Filename"],
            "Relevance Score (%)": f"{score_float:.2f}%",
            "Matched Skills": data["Matched Skills"],
            "Missing Skills": data["Missing Skills"]
        })

    return final_ranked_data


@router.get("/reports/export-excel", summary="Export Ranked Resumes & Skills to Excel")
async def export_excel_report():
    """Delegates to the service layer to generate and stream an Excel file."""
    ranked_data = _prepare_ranked_data()
    if ranked_data is None:
        return {"error": "No job description or resumes have been uploaded."}
    
    excel_buffer = generate_excel_report(ranked_data)
    
    return StreamingResponse(
        content=excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=resume_insights.xlsx"}
    )


@router.get("/reports/export-csv", summary="Export Ranked Resumes & Skills to CSV")
async def export_csv_report():
    """Delegates to the service layer to generate and stream a CSV file."""
    ranked_data = _prepare_ranked_data()
    if ranked_data is None:
        return {"error": "No job description or resumes have been uploaded."}
    
    csv_buffer = generate_csv_report(ranked_data)
    
    return StreamingResponse(
        content=csv_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=resume_insights.csv"}
    )


@router.get("/reports/download-resumes-zip", summary="Download all remaining ranked resumes as a ZIP file")
async def download_remaining_resumes():
    """
    Creates a ZIP archive containing all resume files currently present in the ranked list (db['resumes']).
    """
    if not db.get("resumes"):
        return {"error": "No resumes remain in the current ranked list to download."}

    # The service function expects the list of resume dictionaries from the data store
    zip_buffer = generate_resumes_zip(db["resumes"])

    return StreamingResponse(
        content=zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=Remaining_Resumes.zip"}
    )
