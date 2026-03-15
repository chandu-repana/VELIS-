from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="technical")  # technical, behavioral, situational
    difficulty = Column(String(50), default="medium")
    related_skill = Column(String(255), nullable=True)       # Which skill this tests
    order_index = Column(Integer, nullable=False, default=0) # Question number in interview
    audio_file_path = Column(String(500), nullable=True)     # TTS audio file
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    response = relationship("Response", back_populates="question", uselist=False)

    def __repr__(self):
        return f"<Question {self.order_index} type={self.question_type}>"