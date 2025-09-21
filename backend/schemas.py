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
    parsed_skills: Optional[List[str]] = None

class FeedbackRequest(BaseModel):
    suggestion_id: str
    job_title: str
    user_id: str
    rating: str # e.g., "helpful" or "not_helpful"

# --- V3 Schemas: Detailed Skills ---
class SkillRequirementsRequest(BaseModel):
    job_title: str

class SkillRequirementsResponse(BaseModel):
    technical_skills: List[str]
    soft_skills: List[str]
    tool_skills: List[str]

# --- V3 Schemas: Career Path ---
class CareerPathRequest(BaseModel):
    current_skills: List[str]
    target_job: str

class CareerPathResponse(BaseModel):
    next_skills: List[str]
    milestones: List[str]
    recommended_actions: List[str]