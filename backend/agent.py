import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuration ---
# It's good practice for the agent to manage its own configuration
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in the .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# Use the model that we confirmed works for your project
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')


# --- The Agent's Core Function ---
def analyze_skills_for_job(skills: list[str], job_title: str) -> dict:
    """
    Analyzes a list of skills for a given job title using the Gemini API.

    Args:
        skills: A list of strings representing the candidate's skills.
        job_title: A string of the target job title.

    Returns:
        A dictionary containing 'matching_skills' and 'missing_skills'.
    """
    
    prompt = f"""
    Analyze the skills of a candidate for a '{job_title}' role.

    Candidate's skills: {json.dumps(skills)}

    Based on the typical requirements for a '{job_title}', identify which of the 
    candidate's skills are a good match and which common skills are missing.

    IMPORTANT: Your response MUST be a valid JSON object, and only the JSON object.
    The JSON object must have two keys: "matching_skills" and "missing_skills".

    Example of a perfect response:
    {{
      "matching_skills": ["Python", "SQL"],
      "missing_skills": ["Deep Learning Frameworks (TensorFlow/PyTorch)", "Cloud Computing (AWS/GCP/Azure)"]
    }}
    """

    print("Agent: Calling the Gemini API...")
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        
        result = json.loads(cleaned_response)
        print("Agent: Successfully parsed JSON response.")
        return result

    except json.JSONDecodeError:
        print("Agent Error: The model did not return valid JSON.")
        # In a real app, you'd want more robust error handling
        return {"matching_skills": [], "missing_skills": ["Error: Could not parse AI response."]}
    except Exception as e:
        print(f"Agent Error: An unexpected error occurred: {e}")
        return {"matching_skills": [], "missing_skills": [f"An unexpected error occurred: {e}"]}