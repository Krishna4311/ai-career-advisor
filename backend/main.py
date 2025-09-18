from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import our custom modules
from schemas import SkillAnalysisRequest, SkillAnalysisResponse
from agent import analyze_skills_for_job

# Create the FastAPI app instance
app = FastAPI(
    title="Personalized AI Career Advisor API",
    description="An API that uses a GenAI agent to perform a skill gap analysis.",
    version="1.0.0"
)

# --- Middleware ---
# Configure CORS (Cross-Origin Resource Sharing)
# This allows our frontend (running on a different URL) to communicate with this backend.
# For a demo, allowing all origins is fine. For production, you'd restrict this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# Add this to main.py
'''
@app.get("/")
def read_root():
    return {"message": "AI Career Advisor API is running"}
'''
# --- API Endpoint ---
@app.post("/api/analyze", response_model=SkillAnalysisResponse)
async def analyze_skills(request: SkillAnalysisRequest):
    """
    Receives a request with skills and a job title,
    passes it to the agent, and returns the analysis.
    """
    try:
        # Call the agent's function to do the actual work
        result_dict = analyze_skills_for_job(
            skills=request.skills, 
            job_title=request.job_title
        )
        return SkillAnalysisResponse(**result_dict)
    except Exception as e:
        # This is a general catch-all for any unexpected errors from the agent
        print(f"API Error: An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred in the AI agent.")
# This must be the LAST line of code in main.py
app.mount("/", StaticFiles(directory="dist", html = True), name="static")