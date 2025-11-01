from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import firebase_admin
from firebase_admin import credentials
import os
import json
import uuid

# schemas
from schemas import (
    SkillAnalysisRequest, SkillAnalysisResponse, 
    JobSuggestionResponse, FeedbackRequest,
    SkillRequirementsRequest, SkillRequirementsResponse,
    CareerPathRequest, CareerPathResponse, SavePathRequest
)
# agent functions
from agent import (
    analyze_skills_for_job, get_job_suggestions, 
    get_skills_for_job, generate_career_path,
    extract_skills_from_text, normalize_input,
    parse_resume_structure,
    extract_skills_from_structured_data
)
# services
from resume_parser import parse_resume
from database import save_user_skills, save_feedback, save_career_path, get_saved_paths
from auth_utils import get_current_user
from auth import router as auth_router

if not firebase_admin._apps:
    service_account_json_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    cred = None

    if service_account_json_str:
        print("Initializing Firebase Admin SDK from environment variable.")
        service_account_info = json.loads(service_account_json_str)
        cred = credentials.Certificate(service_account_info)
    else:
        print("Initializing Firebase Admin SDK from local file 'serviceAccountKey.json'.")
        try:
            cred = credentials.Certificate("serviceAccountKey.json")
        except FileNotFoundError:
            print("\n!!! WARNING: serviceAccountKey.json not found. Backend auth features (token verification) will fail. !!!\n")
        except Exception as e:
            print(f"\n!!! ERROR: Failed to load serviceAccountKey.json: {e} !!!\n")

    if cred:
        try:
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
        except Exception as e:
             print(f"\n!!! ERROR: Firebase Admin SDK initialization failed: {e} !!!\n")
    else:
        print("\n!!! ERROR: Could not load Firebase credentials. Backend auth features will fail. !!!\n")

app = FastAPI(title="Career Craft API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


# --- API ENDPOINTS ---
# --- V3 PROTECTED ENDPOINTS ---
@app.post("/api/generate-path", response_model=CareerPathResponse, tags=["V3 Features - Protected"])
async def generate_career_path_endpoint(
    request: CareerPathRequest, 
    current_user: dict = Depends(get_current_user) 
):
    user_id = current_user['uid']
    result_dict = generate_career_path(
        current_skills=request.current_skills,
        target_job=request.target_job
    )
    return CareerPathResponse(**result_dict)

@app.post("/api/get-skills-for-job", response_model=SkillRequirementsResponse, tags=["V3 Features - Protected"])
async def get_detailed_skills(
    request: SkillRequirementsRequest,
    current_user: dict = Depends(get_current_user) 
):
    user_id = current_user['uid'] 
    result_dict = get_skills_for_job(job_title=request.job_title)
    return SkillRequirementsResponse(**result_dict)

@app.post("/api/save-path", tags=["V3 Features - Protected"])
async def save_path(request: SavePathRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['uid']
    save_career_path(
        user_id=user_id,
        target_job=request.target_job,
        path_data=request.path_data.dict()
    )
    return {"status": "success", "message": "Path saved successfully."}

@app.get("/api/my-paths", tags=["V3 Features - Protected"])
async def get_my_paths(current_user: dict = Depends(get_current_user)):
    user_id = current_user['uid']
    paths = get_saved_paths(user_id=user_id)
    return {"paths": paths}

# --- V2 PUBLIC ENDPOINTS ---
@app.post("/api/suggest-jobs", response_model=JobSuggestionResponse, tags=["V2 Features - Protected"]) 
async def suggest_jobs(
    resume_file: UploadFile = File(None), 
    skills: str = Form(None), 
    current_user: dict = Depends(get_current_user) 
):
    user_id = current_user['uid']
    
    content_for_agent = ""
    skills_to_save = []
    
    if resume_file:
        resume_text = await parse_resume(resume_file)
        extracted_skills = [s.strip() for s in resume_text.split('\n') if len(s.strip()) > 1] 
        content_for_agent = ", ".join(extracted_skills)
        skills_to_save = extracted_skills
    elif skills:
        content_for_agent = skills
        skills_to_save = [s.strip() for s in skills.split(',')]
    else:
        raise HTTPException(status_code=400, detail="Please provide either a resume or skills.")
    
    save_user_skills(user_id=user_id, skills=skills_to_save) 
    
    suggestions_result = await get_job_suggestions(content_for_agent)
    suggestions_result['parsed_skills'] = skills_to_save
    
    return suggestions_result

@app.post("/api/feedback", tags=["V2 Features - Protected"]) 
async def handle_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user) 
):
    user_id = current_user['uid'] 

    save_feedback(
        suggestion_id=request.suggestion_id,
        job_title=request.job_title,
        user_id=user_id,
        rating=request.rating
    )
    return {"status": "success", "message": "Feedback received"}

# --- V1 PROTECTED ENDPOINT ---
@app.post("/api/analyze", response_model=SkillAnalysisResponse, tags=["V1 Features - Protected"])
async def analyze_skills(
    request: SkillAnalysisRequest,
    current_user: dict = Depends(get_current_user) 
):
    user_id = current_user['uid'] 
    result_dict = analyze_skills_for_job(skills=request.skills, job_title=request.job_title)
    return SkillAnalysisResponse(**result_dict)


# --- SERVE FRONTEND ---
app.mount("/", StaticFiles(directory="dist", html=True), name="static")
