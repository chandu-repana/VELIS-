from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class QuestionType(str, enum.Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    GENERAL = "general"


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), default=QuestionType.GENERAL)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    skill_tag = Column(String(100), nullable=True)
    order_index = Column(Integer, default=0)
    audio_path = Column(String(500), nullable=True)

    interview = relationship("Interview", back_populates="questions")
    response = relationship("Response", back_populates="question", uselist=False)

    def __repr__(self):
        return f"<Question id={self.id} type={self.question_type}>"
