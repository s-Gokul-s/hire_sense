

# Import the main FastAPI class
from fastapi import FastAPI 
# Import the routers for different parts of your application
from app.routes import resume
from app.routes import jd
from app.routes import matcher

# Create a FastAPI application instance with a descriptive title for the docs
app = FastAPI(title="HireSense AI Resume Shortlister")

# Define a root endpoint to confirm the API is running
@app.get("/")
def read_root():
    return {"message": "Hiresense backend is running 🚀"}

# --- Include all the application routers ---

# Include the router for job description endpoints (e.g., /upload-jd)
# The 'tags' argument groups these endpoints in the API documentation for clarity.
app.include_router(jd.router, tags=["Job Description"])

# Include the router for resume endpoints (e.g., /upload-resumes)
app.include_router(resume.router, tags=["Resumes"])

# Include the router for the matching engine (e.g., /match, /reset)
# This makes the matching logic available as API endpoints.
app.include_router(matcher.router, tags=["Matching Engine"])