from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class InterviewCreate(BaseModel):
    resume_id: Optional[UUID] = None
    job_role: str = Field(..., min_length=2, max_length=255)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    total_questions: int = Field(default=5, ge=1, le=20)


class InterviewResponse(BaseModel):
    id: UUID
    user_id: UUID
    resume_id: Optional[UUID]
    job_role: Optional[str]
    difficulty: str
    status: str
    total_questions: int
    completed_questions: int
    overall_score: Optional[float]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: UUID
    question_text: str
    question_type: str
    difficulty: str
    related_skill: Optional[str]
    order_index: int

    class Config:
        from_attributes = True