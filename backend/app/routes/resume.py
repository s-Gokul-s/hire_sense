# FastAPI Route to Upload and Extract Text from Resumes

from fastapi import APIRouter,UploadFile,File # FastAPI tools for routing and file uploads
from typing import List # Type hint for a list of files
from app.services.textextract_service import extract_text_from_pdf_file # Import the function to extract text from a PDF file 

# Create a router for the resume endpoint
router = APIRouter()
# Define the endpoint for uploading a resume
@router.post("/upload-resumes/")

async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload one or more resume PDF files and extract their text content.
    Args:
        files (List[UploadFile]): List of uploaded PDF files.
    Returns:
        List[dict]: List of dictionaries containing filename and extracted text.
    """
    extracted_data=[]
    for file in files:
        # Read and extract text content from the uploaded PDF file
        content = extract_text_from_pdf_file(file.file)
        extracted_data.append({
            "source": file,
            "filename": file.filename,
            "content": content
        })
    return extracted_data
