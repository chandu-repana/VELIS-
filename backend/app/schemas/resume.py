from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    file_size: Optional[int]
    extracted_skills: Optional[List[str]]
    experience_years: Optional[int]
    is_parsed: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeSkillsResponse(BaseModel):
    resume_id: UUID
    skills: List[str]
    experience_years: Optional[int]
    education: Optional[Any]
    work_experience: Optional[Any]