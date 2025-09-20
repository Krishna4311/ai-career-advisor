from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
import uuid

# Import schemas for both V1 and V2
from schemas import SkillAnalysisRequest, SkillAnalysisResponse, JobSuggestionResponse, FeedbackRequest
# Import agent functions for both V1 and V2
from agent import analyze_skills_for_job, get_job_suggestions
from resume_parser import parse_resume
from database import save_user_skills, save_feedback

app = FastAPI(title="AI Career Advisor API", version="2.0.0")

# Note: CORS is not strictly needed for single-server mode, but doesn't hurt.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- V1 API ENDPOINT ---
@app.post("/api/analyze", response_model=SkillAnalysisResponse)
async def analyze_skills(request: SkillAnalysisRequest):
    result_dict = analyze_skills_for_job(
        skills=request.skills, 
        job_title=request.job_title
    )
    return SkillAnalysisResponse(**result_dict)

# --- V2 API ENDPOINTS ---
@app.post("/api/suggest-jobs", response_model=JobSuggestionResponse)
async def suggest_jobs(resume_file: UploadFile = File(None), skills: str = Form(None)):
    user_id = str(uuid.uuid4())
    content_for_agent = ""
    skills_to_save = []

    if resume_file:
        content_for_agent = await parse_resume(resume_file)
        skills_to_save.append(content_for_agent[:5000])
    elif skills:
        content_for_agent = skills
        skills_to_save = [s.strip() for s in skills.split(',')]
    else:
        raise HTTPException(status_code=400, detail="Please provide either a resume or skills.")

    save_user_skills(user_id=user_id, skills=skills_to_save)
    return await get_job_suggestions(content_for_agent)

@app.post("/api/feedback")
async def handle_feedback(request: FeedbackRequest):
    save_feedback(
        suggestion_id=request.suggestion_id,
        job_title=request.job_title,
        user_id=request.user_id,
        rating=request.rating
    )
    return {"status": "success", "message": "Feedback received"}

# This must be the LAST line to serve the frontend
app.mount("/", StaticFiles(directory="dist", html=True), name="static")