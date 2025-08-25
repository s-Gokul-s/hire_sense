from fastapi import FastAPI # Import FastAPI class to create the app
from app.routes import resume # Import the resume router from your routes package
from app.routes import jd # Import the job description router from your routes package

# Create a FastAPI application instance
app =FastAPI()


# Create a FastAPI application instance
@app.get("/")
def read_root():
    return {"message": "Hiresense backend is running 🚀"}

# Include the resume router (all resume-related routes are now active)
app.include_router(resume.router)
# Include the job description router (all job description-related routes are now active)
app.include_router(jd.router)

