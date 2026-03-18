from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ResponseOut(BaseModel):
    id: int
    question_id: int
    interview_id: int
    audio_path: Optional[str]
    transcribed_text: Optional[str]
    score: Optional[float]
    feedback: Optional[str]
    strengths: List[str]
    improvements: List[str]
    is_evaluated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TranscriptionResult(BaseModel):
    question_id: int
    interview_id: int
    transcribed_text: str
    language: str
    response_id: int
    message: str
