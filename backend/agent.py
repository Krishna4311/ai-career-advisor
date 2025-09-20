import os
import json
import uuid
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in the .env file.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')


# --- V1 AGENT FUNCTION: SKILL GAP ANALYSIS ---
def analyze_skills_for_job(skills: list[str], job_title: str) -> dict:
    """
    Analyzes a list of skills for a given job title using the Gemini API.
    """
    prompt = f"""
    Analyze the skills of a candidate for a '{job_title}' role.
    Candidate's skills: {json.dumps(skills)}
    Your response MUST be a valid JSON object with two keys: "matching_skills" and "missing_skills".

    Example:
    {{
      "matching_skills": ["Python", "SQL"],
      "missing_skills": ["Deep Learning Frameworks (TensorFlow/PyTorch)"]
    }}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Agent V1 Error: An unexpected error occurred: {e}")
        return {"matching_skills": [], "missing_skills": ["An error occurred."]}


# --- V2 AGENT FUNCTION: JOB SUGGESTIONS ---
async def get_job_suggestions(skills_content: str | list) -> dict:
    """
    Takes either a string of resume text or a list of skills and gets job suggestions.
    """
    prompt = f"""
    You are an expert career recruiter. Analyze the following skills/experience:
    ---
    {skills_content}
    ---
    Suggest 5 relevant job titles. For each, provide a "match_score" (1-100) and a unique "suggestion_id".
    Your response MUST be a valid JSON object with one key: "suggestions".
    """
    response = await model.generate_content_async(prompt)
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
    result = json.loads(cleaned_response)
    for suggestion in result.get("suggestions", []):
        suggestion["suggestion_id"] = f"sugg_{uuid.uuid4()}"
    return result