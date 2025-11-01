import os
import json
import uuid
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from database import get_cached_job_skills, cache_job_skills

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in the .env file.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-flash-latest')

# ---  Generation Configs ---
JSON_CONFIG = GenerationConfig(
    temperature=0.2,
    response_mime_type="application/json"
)

SKILL_CONFIG = GenerationConfig(
    temperature=0.0
)

CREATIVE_JSON_CONFIG = GenerationConfig(
    temperature=0.5,
    response_mime_type="application/json"
)

def analyze_skills_for_job(skills: list[str], job_title: str) -> dict:
    """Analyzes skills for a job."""
    prompt = f"""
    You are a skills analyst. Compare the following skills with the typical requirements for a '{job_title}'.

    Skills: {', '.join(skills)}

    Return a JSON object with two keys: "matching_skills" and "missing_skills".
    """
    try:
        response = model.generate_content(prompt, generation_config=JSON_CONFIG)
        parsed_json = json.loads(response.text)
        print(f"Parsed JSON (analyze_skills_for_job): {parsed_json}")
        return parsed_json
    except Exception as e:
        print(f"Agent Error (analyze_skills_for_job): {e}")
        return {"matching_skills": [], "missing_skills": []}

def get_job_suggestions(resume_text: str) -> dict:
    """Gets job suggestions based on a resume."""
    prompt = f"""
    You are a career advisor. Based on the following resume text, suggest 5 job titles that would be a good fit.

    Resume Text:
    ---
    {resume_text[:4000]}
    ---

    Return a JSON object with a single key "suggestions", which is a list of objects. Each object should have two keys: "job_title" (string) and "match_score" (an integer between 0 and 100).
    """
    try:
        response = model.generate_content(prompt, generation_config=CREATIVE_JSON_CONFIG)
        suggestions_data = json.loads(response.text) 
        for suggestion in suggestions_data.get("suggestions", []):
            suggestion["suggestion_id"] = str(uuid.uuid4())
        return suggestions_data
    except Exception as e:
        print(f"Agent Error (get_job_suggestions): {e}")
        return {"suggestions": []}

def get_skills_for_job(job_title: str) -> dict:
    """
    Gets skills for a job, using a cache to avoid redundant API calls.
    """
    
    cached_skills = get_cached_job_skills(job_title)
    if cached_skills:
        return cached_skills

    print(f"Calling Gemini API for job: {job_title}")
    prompt = f"""
    You are a job market analyst. What are the technical, soft,
    and tool skills for a '{job_title}'?

    Return a JSON object with three keys: "technical_skills",
    "soft_skills", and "tool_skills". Each key should have a list of strings
    as its value.
    """

    try:
        response = model.generate_content(prompt, generation_config=JSON_CONFIG)
        
        skills_data = json.loads(response.text)

        if skills_data: 
            cache_job_skills(job_title, skills_data)

        return skills_data

    except Exception as e:
        print(f"Agent Error (get_skills_for_job): {e}")
        return {"technical_skills": [], "soft_skills": [], "tool_skills": []}

def generate_career_path(current_skills: list[str], target_job: str) -> dict:
    """Generates a career path."""
    prompt = f"""
    You are a career strategist. My current skills are: {', '.join(current_skills)}. My target job is '{target_job}'.

    Generate a career path with milestones, skills to learn next, and recommended actions.

    Return a JSON object with three keys: "milestones", "next_skills", and "recommended_actions".
    Each key must contain a list of strings. For example:
    {{
      "milestones": ["Achieve proficiency in Python", "Build a portfolio of 3 data science projects"],
      "next_skills": ["SQL", "Tableau", "Scikit-learn"],
      "recommended_actions": ["Take an online course in machine learning", "Network with data scientists on LinkedIn"]
    }}
    """
    try:
        response = model.generate_content(prompt, generation_config=CREATIVE_JSON_CONFIG)
        return json.loads(response.text) # Direct parsing
    except Exception as e:
        print(f"Agent Error (generate_career_path): {e}")
        return {"milestones": [], "next_skills": [], "recommended_actions": []}

def extract_skills_from_text(text: str) -> list[str]:
    """
    Extracts skills from any block of text.
    This function replaces the duplicated skill extractors.
    """
    if not text or text.isspace():
        return []
        
    prompt = f"""
    You are an expert skill extractor. From the following text, extract a clean list of all technical and soft skills.

    Your response MUST be a single line of comma-separated values.

    Text to Analyze:
    ---
    {text}
    ---

    Example Response: Python, React, SQL, Teamwork, Communication, Git, Docker
    """
    try:
        response = model.generate_content(prompt, generation_config=SKILL_CONFIG)
        return [s.strip() for s in response.text.strip().split(',') if s.strip()]
    except Exception as e:
        print(f"Agent Error (extract_skills_from_text): {e}")
        return []

def parse_resume_structure(resume_text: str) -> dict:
    """Step 1: Parses raw resume text into a structured JSON."""
    prompt = f"""
    You are an expert resume parser. Analyze the following resume text and structure it into a JSON object with keys like "education", "experience", and "skills".

    Resume Text:
    ---
    {resume_text[:4000]}
    ---

    Return only the JSON object.
    """
    print("Agent: Calling Gemini for Step 1 - Resume Structuring...")
    try:
        response = model.generate_content(prompt, generation_config=JSON_CONFIG)
        return json.loads(response.text) 
    except Exception as e:
        print(f"Agent Error (Step 1): {e}")
        return {}

def extract_skills_from_structured_data(resume_json: dict) -> list[str]:
    """
    Step 2: Extracts skills from the structured JSON resume data.
    This now calls the single, consolidated skill extractor function.
    """
    print("Agent: Calling Gemini for Step 2 - Skill Extraction...")
    skills_section = resume_json.get("skills", "")
    experience_section = resume_json.get("experience", "")
    
    combined_text = f"Skills Section: {str(skills_section)}\nExperience Section: {str(experience_section)}"
    
    return extract_skills_from_text(combined_text)
