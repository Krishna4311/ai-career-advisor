from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import firebase_admin
from firebase_admin import credentials
import os
import json
import uuid

# Import all schemas
from schemas import (
    SkillAnalysisRequest, SkillAnalysisResponse, 
    JobSuggestionResponse, FeedbackRequest,
    SkillRequirementsRequest, SkillRequirementsResponse,
    CareerPathRequest, CareerPathResponse
)
# Import all agent functions
from agent import (
    analyze_skills_for_job, get_job_suggestions, 
    get_skills_for_job, generate_career_path,
    extract_skills_from_text, normalize_input
)
# Import other services
from resume_parser import parse_resume, parse_resume_structure, extract_skills_from_structured_data
from database import save_user_skills, save_feedback
from auth import router as auth_router

# --- Firebase Admin SDK Initialization ---
if not firebase_admin._apps:
    # Check for the service account key in environment variables
    service_account_json_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if service_account_json_str:
        service_account_info = json.loads(service_account_json_str)
        cred = credentials.Certificate(service_account_info)
    else:
        # Fallback to the local file for development (optional, but requires .env)
        cred = credentials.Certificate("serviceAccountKey.json")
    
    firebase_admin.initialize_app(cred)

app = FastAPI(title="Career Craft API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# authentication router for signup/login
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


# --- API ENDPOINTS ---

# --- V3 PUBLIC ENDPOINTS ---
@app.post("/api/generate-path", response_model=CareerPathResponse, tags=["V3 Features"])
async def generate_career_path_endpoint(request: CareerPathRequest):
    result_dict = generate_career_path(
        current_skills=request.current_skills, 
        target_job=request.target_job
    )
    return CareerPathResponse(**result_dict)

@app.post("/api/get-skills-for-job", response_model=SkillRequirementsResponse, tags=["V3 Features"])
async def get_detailed_skills(request: SkillRequirementsRequest):
    result_dict = get_skills_for_job(job_title=request.job_title)
    return SkillRequirementsResponse(**result_dict)

# --- V2 PUBLIC ENDPOINTS ---
@app.post("/api/suggest-jobs", response_model=JobSuggestionResponse, tags=["V2 Features"])
async def suggest_jobs(resume_file: UploadFile = File(None), skills: str = Form(None)):
    user_id = str(uuid.uuid4()) # Placeholder user ID for this public feature
    content_for_agent = ""
    skills_to_save = []
    if resume_file:
        resume_text = await parse_resume(resume_file)
        structured_resume = parse_resume_structure(resume_text)
        extracted_skills = extract_skills_from_structured_data(structured_resume)
        
        # Fallback to basic text splitting if AI fails
        if not extracted_skills:
            print("AI skill extraction failed. Falling back to basic text parsing.")
            extracted_skills = [s.strip() for s in resume_text.split('\n') if s.strip()]

        content_for_agent = ", ".join(extracted_skills)
        skills_to_save = extracted_skills
    elif skills:
        content_for_agent = skills
        skills_to_save = [s.strip() for s in skills.split(',')]
    else:
        raise HTTPException(status_code=400, detail="Please provide either a resume or skills.")
    
    save_user_skills(user_id=user_id, skills=skills_to_save)
    suggestions_result = get_job_suggestions(content_for_agent)
    
    suggestions_result['parsed_skills'] = skills_to_save
    
    return suggestions_result

@app.post("/api/feedback", tags=["V2 Features"])
async def handle_feedback(request: FeedbackRequest):
    save_feedback(
        suggestion_id=request.suggestion_id,
        job_title=request.job_title,
        user_id=request.user_id,
        rating=request.rating
    )
    return {"status": "success", "message": "Feedback received"}

# --- V1 PUBLIC ENDPOINT ---
@app.post("/api/analyze", response_model=SkillAnalysisResponse, tags=["V1 Features"])
async def analyze_skills(request: SkillAnalysisRequest):
    result_dict = analyze_skills_for_job(skills=request.skills, job_title=request.job_title)
    return SkillAnalysisResponse(**result_dict)


# --- SERVE FRONTEND ---
app.mount("/", StaticFiles(directory="dist", html=True), name="static")
