from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials
import os
import json

# Schemas
from schemas import (
    SkillAnalysisRequest, SkillAnalysisResponse,
    JobSuggestionResponse, FeedbackRequest,
    SkillRequirementsRequest, SkillRequirementsResponse,
    CareerPathRequest, CareerPathResponse, SavePathRequest
)
# Agent functions
from agent import (
    analyze_skills_for_job, get_job_suggestions,
    get_skills_for_job, generate_career_path
)
# Services
from resume_parser import parse_resume
from database import save_user_skills, save_feedback, save_career_path, get_saved_paths, delete_saved_path
from auth_utils import get_current_user
from auth_routes import router as auth_router

# --- Firebase Admin SDK Initialization ---
if not firebase_admin._apps:
    service_account_json_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    cred = None

    if service_account_json_str and service_account_json_str.strip():
        print("Initializing Firebase Admin SDK from environment variable.")
        try:
            service_account_info = json.loads(service_account_json_str)
            cred = credentials.Certificate(service_account_info)
        except json.JSONDecodeError as e:
            print(f"\n!!! FATAL ERROR: Invalid JSON in FIREBASE_SERVICE_ACCOUNT_JSON env var: {e} !!!\n")
            raise e
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
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Career Craft"}

# --- CORS Configuration ---
origins = [
    "https://pcsr-v2.web.app",     
    "http://localhost:5173",     
]
service_url = os.getenv("SERVICE_URL", "https://ai-career-advisor-200369475119.us-central1.run.app")
if service_url not in origins:
    origins.append(service_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# --- API ENDPOINTS ---
api_router = APIRouter()


@api_router.post("/generate-path", response_model=CareerPathResponse, tags=["V3 Features - Protected"])
async def generate_career_path_endpoint(
    request: CareerPathRequest,
    current_user: dict = Depends(get_current_user)
):
    result_dict = generate_career_path(
        current_skills=request.current_skills,
        target_job=request.target_job
    )
    return CareerPathResponse(**result_dict)

@api_router.post("/get-skills-for-job", response_model=SkillRequirementsResponse, tags=["V3 Features - Protected"])
async def get_detailed_skills(
    request: SkillRequirementsRequest,
    current_user: dict = Depends(get_current_user)
):
    result_dict = get_skills_for_job(job_title=request.job_title)
    return SkillRequirementsResponse(**result_dict)

@api_router.post("/save-path", tags=["V3 Features - Protected"])
async def save_path(request: SavePathRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['uid']
    save_career_path(
        user_id=user_id,
        target_job=request.target_job,
        path_data=request.path_data.dict()
    )
    return {"status": "success", "message": "Path saved successfully."}

@api_router.get("/my-paths", tags=["V3 Features - Protected"])
async def get_my_paths(current_user: dict = Depends(get_current_user)):
    user_id = current_user['uid']
    paths = get_saved_paths(user_id=user_id)
    return {"paths": paths}

@api_router.delete("/my-paths/{path_id}", tags=["V3 Features - Protected"])
async def delete_path(path_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user['uid']
    try:
        delete_saved_path(user_id=user_id, path_id=path_id)
        return {"status": "success", "message": "Path deleted successfully."}
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "permission" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")
        
@api_router.post("/suggest-jobs", response_model=JobSuggestionResponse, tags=["V2 Features - Protected"])
async def suggest_jobs(
    resume_file: UploadFile = File(None),
    skills: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user['uid']
    skills_to_save = []
    suggestions_result = {}

    try:
        if resume_file:
            resume_text = await parse_resume(resume_file)
            if not resume_text or resume_text.isspace():
                raise HTTPException(status_code=422, detail="Failed to extract any text from the uploaded resume. The file might be empty, scanned, or in an unsupported format.")

            extracted_skills = [s.strip() for s in resume_text.split('\n') if len(s.strip()) > 1]
            skills_to_save = extracted_skills
            suggestions_result = await get_job_suggestions(resume_text)

        elif skills:
            content_for_agent = skills
            skills_to_save = [s.strip() for s in skills.split(',') if s.strip()]
            suggestions_result = await get_job_suggestions(content_for_agent)

        else:
            raise HTTPException(status_code=400, detail="Please provide either a resume file or a list of skills.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"!!! UNHANDLED CRITICAL ERROR in suggest_jobs endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred while processing the request. Please check the backend logs for more information.")

    if not suggestions_result or not suggestions_result.get("suggestions"):
        raise HTTPException(status_code=404, detail="The AI advisor could not generate job suggestions for the provided input. Please try a different resume or be more specific with your skills.")

    if skills_to_save:
        save_user_skills(user_id=user_id, skills=skills_to_save)

    suggestions_result['parsed_skills'] = skills_to_save
    return suggestions_result

@api_router.post("/feedback", tags=["V2 Features - Protected"])
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

@api_router.post("/analyze", response_model=SkillAnalysisResponse, tags=["VList Features - Protected"])
async def analyze_skills(
    request: SkillAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    result_dict = analyze_skills_for_job(skills=request.skills, job_title=request.job_title)
    return SkillAnalysisResponse(**result_dict)

app.include_router(api_router, prefix="/api")