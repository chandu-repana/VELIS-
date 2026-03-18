from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class InterviewCreate(BaseModel):
    resume_id: int
    job_role: Optional[str] = "Software Developer"
    num_questions: Optional[int] = 10
    title: Optional[str] = "Interview Session"


class InterviewOut(BaseModel):
    id: int
    user_id: int
    resume_id: Optional[int]
    title: str
    job_role: Optional[str]
    status: str
    overall_score: Optional[float]
    total_questions: int
    answered_questions: int
    created_at: datetime

    model_config = {"from_attributes": True}


class InterviewStartResponse(BaseModel):
    interview_id: int
    title: str
    job_role: str
    total_questions: int
    message: str
