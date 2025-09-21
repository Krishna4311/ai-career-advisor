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

# --- NEW NLP FUNCTION: NORMALIZE/CLEAN USER INPUT ---
def normalize_input(input_data: str | list[str]) -> str | list[str]:
    """
    Uses the Gemini API to correct spelling and standardize job titles or skills.
    """
    is_list = isinstance(input_data, list)
    context = "a list of skills" if is_list else "a job title"
    output_format = "a JSON array of strings" if is_list else "a single string"
    
    prompt = f"""
    You are an expert data cleaner. Your task is to correct spelling mistakes, expand abbreviations, and standardize the following {context}.

    Input: {json.dumps(input_data) if is_list else input_data}
    ---
    Return only the cleaned, standardized text in the format of {output_format}. Do not add any other commentary or explanation.
    """
    print(f"Agent: Calling Gemini API for input normalization on: {input_data}")
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.0)
        )
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response) if is_list else cleaned_response
    except Exception as e:
        print(f"Agent Error: An unexpected error occurred during normalization: {e}")
        return input_data # On failure, return the original input


# --- NEW AI-POWERED SKILL EXTRACTOR ---
def extract_skills_from_text(resume_text: str) -> list[str]:
    """
    Uses the Gemini API to extract a list of skills from raw resume text.
    """
    prompt = f"""
    You are an expert technical recruiter. Analyze the following resume text and extract a list of all the technical skills, soft skills, and tools mentioned.

    Your response MUST be a valid JSON object with a single key \"skills\", which contains a flat list of strings. Do not include any other text or formatting.

    Resume Text:
    ---
    {resume_text[:4000]}
    ---

    Example of a perfect response:
    {{
      \"skills\": [\"Python\", \"React\", \"SQL\", \"Teamwork\", \"Communication\", \"Git\", \"Docker\"]
    }}
    """
    print("Agent: Calling Gemini API for AI-powered skill extraction...")
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.0)
        )
        
        # More resilient JSON parsing
        text_response = response.text.strip()
        json_start = text_response.find('{')
        json_end = text_response.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = text_response[json_start:json_end]
            result = json.loads(json_str)
            return result.get("skills", [])
        else:
            print("Agent Error: No JSON object found in the AI response.")
            return [] # Return empty list if no JSON is found

    except Exception as e:
        print(f"Agent Error: An unexpected error occurred during skill extraction: {e}")
        return [] # Return empty list on failure


# --- NEW V3 AGENT FUNCTION: CAREER PATH GENERATION ---
# In backend/agent.py

def generate_career_path(current_skills: list[str], target_job: str) -> dict:
    """
    Generates a multi-part career path from a user's skills to a target job.
    """
    prompt = f"""
    You are a world-class career coach and senior technical recruiter.
    A user has the following skills: {json.dumps(current_skills)}.
    Their target job is: "{target_job}".

    Create a comprehensive, actionable career path for them.

    Your response MUST be a valid JSON object, and only the JSON object.
    The JSON object must have three keys: "next_skills", "milestones", and "recommended_actions".
    - "next_skills": A list of the top 4 most critical skills they should learn next.
    - "milestones": A list of 2-3 intermediate job titles that form a typical career ladder to their target job.
    - "recommended_actions": A list of 3 practical, actionable steps. **IMPORTANT: This advice must be generic. Do NOT mention specific names of course instructors, websites (e.g., Coursera, Kaggle), or specific commercial products unless they are industry standards (e.g., AWS, Docker).**

    Example of a perfect response for a user with basic Python skills targeting "Cloud Engineer":
    {{
      "next_skills": ["Cloud platform fundamentals", "Infrastructure as Code", "Containerization basics", "Linux command line"],
      "milestones": ["IT Support Specialist", "Junior Cloud Administrator", "Cloud Engineer"],
      "recommended_actions": ["Earn a foundational cloud certification", "Build a personal project on a major cloud platform and host it", "Contribute to an open-source project that uses cloud infrastructure"]
    }}
    """
    print(f"Agent V3: Calling Gemini API for career path to '{target_job}'...")
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Agent V3 Error: An unexpected error occurred: {e}")
        return {"next_skills": [], "milestones": [], "recommended_actions": ["An error occurred."]}

# --- NEW V3 AGENT FUNCTION: DETAILED SKILL REQUIREMENTS ---
def get_skills_for_job(job_title: str) -> dict:
    """
    Analyzes a job title and returns a detailed breakdown of required skills.
    """
    prompt = f"""
    You are a senior hiring manager and tech recruiter.
    Provide a detailed breakdown of the most critical skills required for the job title: "{job_title}".

    Your response MUST be a valid JSON object, and only the JSON object.
    The JSON object must have three keys: "technical_skills", "soft_skills", and "tool_skills".
    Each key should have a list of 5-7 relevant skills as strings.

    Example of a perfect response:
    {{
      "technical_skills": ["Cloud Computing (AWS/GCP)", "Infrastructure as Code (Terraform)", "CI/CD Pipelines"],
      "soft_skills": ["Problem Solving", "Communication", "Collaboration"],
      "tool_skills": ["Kubernetes", "Docker", "Git", "Jenkins"]
    }}
    """
    print(f"Agent V3: Calling Gemini API for skills breakdown of '{job_title}'...")
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Agent V3 Error: An unexpected error occurred: {e}")
        return {"technical_skills": [], "soft_skills": [], "tool_skills": ["An error occurred."]}


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
    print("Agent V2: Calling the Gemini API for job suggestions...")
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.1)
        )
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")

        # --- NEW SAFETY CHECK ---
        if not cleaned_response:
            print("Agent V2 Error: Received an empty response from the AI.")
            raise ValueError("Empty response from AI")

        result = json.loads(cleaned_response)
        for suggestion in result.get("suggestions", []):
            suggestion["suggestion_id"] = f"sugg_{uuid.uuid4()}"

        return result

    except Exception as e:
        print(f"Agent V2 Error: An unexpected error occurred: {e}")
        # Return an empty list to prevent the frontend from crashing
        return {"suggestions": []}


# --- V1 AGENT FUNCTION: SKILL GAP ANALYSIS (IMPROVED) ---
def analyze_skills_for_job(skills: list[str], job_title: str) -> dict:
    """
    Analyzes a list of skills for a given job title using the Gemini API.
    Matching skills are literal, and missing skills are ranked by priority.
    """
    prompt = f"""
    You are a helpful and strict career advisor.
    A user has the following skills: {json.dumps(skills)}.
    Their target job is: "{job_title}".

    Analyze their skills against the job requirements following these strict rules:
    1.  The "matching_skills" list MUST ONLY contain skills from the user's provided list that are relevant to the target job. Do NOT infer or add skills the user did not mention.
    2.  The "missing_skills" list MUST be ordered by priority. The most critical, must-have skills should be at the top, and less important or "nice-to-have" skills should be at the bottom.

    Your response MUST be a valid JSON object with two keys: "matching_skills" and "missing_skills".

    Example of a perfect response for a user with skills ["Python", "Git"] targeting "ML Engineer":
    {{
      "matching_skills": ["Python", "Git"],
      "missing_skills": [
        "Machine Learning Fundamentals (Scikit-learn, Pandas)",
        "Deep Learning Frameworks (TensorFlow/PyTorch)",
        "SQL and Databases",
        "Cloud Computing (AWS/GCP)",
        "Communication and Teamwork"
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")

        if not cleaned_response:
            print("Agent V1 Error: Received an empty response from the AI.")
            raise ValueError("Empty response from AI")
        
        return json.loads(cleaned_response)

    except Exception as e:
        print(f"Agent V1 Error: An unexpected error occurred: {e}")
        return {
            "matching_skills": [], 
            "missing_skills": ["Could not get a valid analysis from the AI. Please try different inputs."]
        }