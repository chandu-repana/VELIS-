from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QuestionOut(BaseModel):
    id: int
    interview_id: int
    text: str
    question_type: str
    difficulty: str
    skill_tag: Optional[str]
    order_index: int
    audio_path: Optional[str]

    model_config = {"from_attributes": True}
