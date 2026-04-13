from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    is_parsed: bool
    message: str


class ResumeParseResponse(BaseModel):
    id: int
    filename: str
    extracted_skills: List[str]
    experience_years: int
    education: List[Dict[str, str]]
    is_parsed: bool
    suggested_role: Optional[str] = None


class ResumeOut(BaseModel):
    id: int
    user_id: int
    filename: str
    file_type: str
    extracted_skills: List[str]
    experience_years: int
    education: List[Dict[str, str]]
    is_parsed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
