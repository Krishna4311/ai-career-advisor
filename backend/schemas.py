from pydantic import BaseModel
from typing import List, Optional

# --- V1 Schemas ---
class SkillAnalysisRequest(BaseModel):
    skills: List[str]
    job_title: str

class SkillAnalysisResponse(BaseModel):
    matching_skills: List[str]
    missing_skills: List[str]

# --- V2 Schemas ---
class JobSuggestion(BaseModel):
    job_title: str
    match_score: int
    suggestion_id: str

class JobSuggestionResponse(BaseModel):
    suggestions: List[JobSuggestion]

# Add this new class to schemas.py
class FeedbackRequest(BaseModel):
    suggestion_id: str
    job_title: str
    user_id: str
    rating: str # e.g., "helpful" or "not_helpful"