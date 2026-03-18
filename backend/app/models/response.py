from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Response(Base, TimestampMixin):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    audio_path = Column(String(500), nullable=True)
    transcribed_text = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    improvements = Column(JSON, default=list)
    duration_seconds = Column(Integer, nullable=True)
    is_evaluated = Column(Boolean, default=False, nullable=False)

    question = relationship("Question", back_populates="response")

    def __repr__(self):
        return f"<Response id={self.id} score={self.score}>"
