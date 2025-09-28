

# Import the main FastAPI class
from fastapi import FastAPI 
# Import the routers for different parts of your application
from app.routes import resume
from fastapi.middleware.cors import CORSMiddleware # Import the CORS middleware
from app.routes import jd
from app.routes import matcher
from app.routes import acceptance
from app.routes import viewer
from app.routes import insights
from app.routes import reports
from app.routes import analytics
# Create a FastAPI application instance with a descriptive title for the docs
app = FastAPI(title="HireSense AI Resume Shortlister")

# Add the CORS middleware here
origins = [
    "http://localhost:5173",  # The URL of your React development server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

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

app.include_router(acceptance.router, tags=["Resume Acceptance"])

app.include_router(viewer.router, tags=["Resume Viewer"])

app.include_router(insights.router, tags=["Insights"])

app.include_router(reports.router,tags=["Reports"])

app.include_router(analytics.router, tags=["Analytics & Dashboard"])