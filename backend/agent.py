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

def _parse_json_from_text(text: str) -> dict:
    """Safely extracts a JSON object from a string."""
    try:
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            return json.loads(text[json_start:json_end])
    except (json.JSONDecodeError, IndexError):
        pass
    return {}

def analyze_skills_for_job(skills: list[str], job_title: str) -> dict:
    """Analyzes skills for a job."""
    prompt = f"""
    You are a skills analyst. Compare the following skills with the typical requirements for a '{job_title}'.

    Skills: {', '.join(skills)}

    Return a JSON object with two keys: "matching_skills" and "missing_skills".
    """
    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.2))
        return _parse_json_from_text(response.text)
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
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.5))
        suggestions_data = _parse_json_from_text(response.text)
        for suggestion in suggestions_data.get("suggestions", []):
            suggestion["suggestion_id"] = str(uuid.uuid4())
        return suggestions_data
    except Exception as e:
        print(f"Agent Error (get_job_suggestions): {e}")
        return {"suggestions": []}

def get_skills_for_job(job_title: str) -> dict:
    """Gets skills for a job."""
    prompt = f"""
    You are a job market analyst. What are the technical, soft, and tool skills for a '{job_title}'?

    Return a JSON object with three keys: "technical_skills", "soft_skills", and "tool_skills". Each key should have a list of strings as its value.
    """
    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.2))
        return _parse_json_from_text(response.text)
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
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.5))
        return _parse_json_from_text(response.text)
    except Exception as e:
        print(f"Agent Error (generate_career_path): {e}")
        return {"milestones": [], "next_skills": [], "recommended_actions": []}

def extract_skills_from_text(text: str) -> list[str]:
    """Extracts skills from text."""
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
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.0))
        return [s.strip() for s in response.text.strip().split(',')]
    except Exception as e:
        print(f"Agent Error (extract_skills_from_text): {e}")
        return []

def normalize_input(text: str) -> str:
    """Normalizes input text."""
    return text

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
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.0))
        return _parse_json_from_text(response.text)
    except Exception as e:
        print(f"Agent Error (Step 1): {e}")
        return {{}}

def extract_skills_from_structured_data(resume_json: dict) -> list[str]:
    """Step 2: Extracts skills from the structured JSON resume data."""
    # Combine relevant text fields for the AI to analyze
    skills_section = resume_json.get("skills", "")
    experience_section = resume_json.get("experience", "")
    combined_text = f"Skills Section: {skills_section}\nExperience Section: {experience_section}"

    prompt = f"""
    You are an expert skill extractor. From the following text, extract a clean list of all technical and soft skills.

    Your response MUST be a single line of comma-separated values.

    Text to Analyze:
    ---
    {combined_text}
    ---

    Example Response: Python, React, SQL, Teamwork, Communication, Git, Docker
    """
    print("Agent: Calling Gemini for Step 2 - Skill Extraction...")
    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.0))
        return [s.strip() for s in response.text.strip().split(',')]
    except Exception as e:
        print(f"Agent Error (Step 2): {e}")
        return []
