import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.services.preprocess_service import preprocess_text
from app.services.embedding_service import generate_embedding
from app.services.prediction_service import prediction_service
from app.services.insights_service import get_skill_matches # import the insights matcher
from app.services.textextract_service import extract_text_from_file # Corrected import to use your service
router = APIRouter()

# Simple in-memory storage for the current session's data
db = {"jd": None, "resumes": []}

# Define storage paths (assuming these are at the project root)
JD_UPLOAD_DIR = "jd_files"
TEMP_RESUME_DIR = "temp_resumes"
ACCEPTED_RESUME_DIR = "accepted_resumes"

# Ensure directories exist (important for the app to run)
os.makedirs(JD_UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_RESUME_DIR, exist_ok=True)
os.makedirs(ACCEPTED_RESUME_DIR, exist_ok=True)

# Helper function to clear a directory
def clear_directory(directory_path: str):
    """Deletes all files and folders within the specified directory."""
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            # Print error but continue to next file
            print(f'Failed to delete {file_path}. Reason: {e}')
            

@router.post("/upload-jd/")
async def upload_jd(file: UploadFile = File(...)):
    """
    Uploads a new Job Description and performs a full session reset, 
    clearing all old JD and temp resume files.
    """
    try:
        # CRITICAL CLEANUP: Clear old JD and temp resume files for a clean slate
        clear_directory(JD_UPLOAD_DIR)
        clear_directory(TEMP_RESUME_DIR)
        
        # Clear the in-memory database
        db["jd"] = None
        db["resumes"] = []

        # Save the new JD file
        jd_filename = file.filename
        file_path = os.path.join(JD_UPLOAD_DIR, jd_filename)
        
        # Save the file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # The extractor needs the file stream and content type.
        # We must re-open the saved file to get the stream.
        with open(file_path, "rb") as saved_file:
            # Pass the file stream and content type to your unified extractor
            content = extract_text_from_file(saved_file, file.content_type)
        
        db["jd"] = {"filename": jd_filename, "content": content}

        return {"filename": jd_filename, "message": "Job Description uploaded and processed successfully. Session reset."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload JD: {e}")

@router.post("/upload-resumes/")
async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Uploads multiple resume files and clears old resumes from the temp directory 
    (if the JD was already uploaded).
    """
    # CRITICAL CLEANUP: Clear old resumes from the temp directory for a clean slate
    clear_directory(TEMP_RESUME_DIR)
    db["resumes"] = [] # Clear the in-memory resume list

    uploaded_files = []
    for file in files:
        try:
            resume_filename = file.filename
            file_path = os.path.join(TEMP_RESUME_DIR, resume_filename)

            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # The extractor needs the file stream and content type.
            # We must re-open the saved file to get the stream.
            with open(file_path, "rb") as saved_file:
                # Pass the file stream and content type to your unified extractor
                content = extract_text_from_file(saved_file, file.content_type)

            db["resumes"].append({"filename": resume_filename, "content": content})
            uploaded_files.append(resume_filename)
            
        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
            continue # Continue to next file if one fails
    
    if not uploaded_files:
        raise HTTPException(status_code=500, detail="No resumes were uploaded successfully.")

    return {"uploaded_files": uploaded_files, "message": f"{len(uploaded_files)} resumes uploaded and processed successfully."}

@router.post("/match/")
async def match_resumes():
    """
    Orchestrates the resume matching process by using the prediction service
    and combines it with insights for a hybrid Fit Score.
    """
    if not db["jd"]:
        raise HTTPException(status_code=404, detail="Job Description not uploaded.")
    if not db["resumes"]:
        raise HTTPException(status_code=404, detail="No resumes uploaded.")

    # Extract content for batch processing
    resume_contents = [resume["content"] for resume in db["resumes"]]
    jd_content = db["jd"]["content"]

    # Get hybrid predictions from the PredictionService
    predictions = prediction_service.predict_batch(resume_contents, jd_content)

    # We will build the ranked list here, but first, ensure the scores are 
    # written back to the original db["resumes"] list for /analytics access.
    ranked_resumes = []
    
    for i, resume in enumerate(db["resumes"]):
        pred = predictions[i]

        # Hybrid fit score from ML + skill insights
        hybrid_score = pred.get("hybrid_fit_score", pred["fit_probability"]) * 100
        prediction_label = pred.get("prediction", "Fit")

        # Extract matched/missing skills for transparency
        skill_breakdown = get_skill_matches(jd_content, resume_contents[i])

        # === FIX: INJECT THE MATCHING DATA INTO THE ORIGINAL DB OBJECT ===
        resume["score"] = round(hybrid_score, 2)
        resume["prediction"] = prediction_label
        resume["matched_skills"] = skill_breakdown["matched_skills"]
        resume["missing_skills"] = skill_breakdown["missing_skills"]
        # ================================================================

        # Add the updated resume object (which now contains score and skills) to the list to be ranked
        ranked_resumes.append(resume)

    # Rank the results by hybrid score (highest first)
    ranked_resumes.sort(key=lambda x: x["score"], reverse=True)

    return {"ranked_resumes": ranked_resumes}


@router.post("/reset/")
async def reset_session():
    """
    Performs a FULL session reset: Clears stored JD/resumes from memory 
    AND deletes all files from jd_files and temp_resumes directories.
    """
    # 1. Clear file system directories
    clear_directory(JD_UPLOAD_DIR)
    clear_directory(TEMP_RESUME_DIR)
    # NOTE: Accepted resumes remain in ACCEPTED_RESUME_DIR until manually moved/deleted.

    # 2. Clear in-memory data
    db["jd"] = None
    db["resumes"] = []
    
    return {"message": "Full session reset complete. All temporary files deleted."}


@router.delete("/reject-resume/{filename}", summary="Removes resume from disk and memory")
async def reject_resume(filename: str):
    """
    Deletes the specified resume file from the 'temp_resumes' folder
    and removes its metadata from the in-memory database.
    """
    # 1. Remove from in-memory list (db["resumes"])
    initial_count = len(db["resumes"])
    db["resumes"] = [r for r in db["resumes"] if r["filename"] != filename]
    if len(db["resumes"]) == initial_count:
        # The resume was not found in the list, but we still try to delete the file
        print(f"Warning: Resume {filename} not found in in-memory list.")

    # 2. Remove file from disk
    file_path = os.path.join(TEMP_RESUME_DIR, filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": f"Resume {filename} rejected and file removed."}
        else:
            # If the file wasn't found, it's still a successful rejection/cleanup
            return {"message": f"Resume {filename} metadata removed. File not found on disk, likely already removed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file {filename}: {e}")

@router.post("/accept-resume/{filename}", summary="Moves resume to the accepted directory")
async def accept_resume(filename: str):
    """
    Moves the specified resume file from the 'temp_resumes' folder
    to the 'accepted_resumes' folder and removes its metadata from the 
    in-memory database (effectively removing it from the ranked list).
    """
    
    # 1. Define source and destination paths
    source_path = os.path.join(TEMP_RESUME_DIR, filename)
    destination_path = os.path.join(ACCEPTED_RESUME_DIR, filename)

    # 2. Check if the file exists in the source (temp) directory
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail=f"Resume file {filename} not found in temporary directory.")

    try:
        # 3. Move the file
        shutil.move(source_path, destination_path)
        
        # 4. Remove from in-memory list (db["resumes"])
        db["resumes"] = [r for r in db["resumes"] if r["filename"] != filename]

        return {"message": f"Resume {filename} accepted and moved to accepted_resumes."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move file {filename}: {e}")
