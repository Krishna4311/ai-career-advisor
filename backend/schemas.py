from pydantic import BaseModel
from typing import List

# This defines the structure of the data we expect IN our API request
class SkillAnalysisRequest(BaseModel):
    skills: List[str]
    job_title: str

# This defines the structure of the data we will send OUT in our API response
class SkillAnalysisResponse(BaseModel):
    matching_skills: List[str]
    missing_skills: List[str]