from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True)
    title = Column(String(255), nullable=True)           # e.g. "Python Developer Interview"
    job_role = Column(String(255), nullable=True)
    difficulty = Column(String(50), default="medium")    # easy, medium, hard
    status = Column(String(50), default="pending")       # pending, active, completed, cancelled
    total_questions = Column(Integer, default=0)
    completed_questions = Column(Integer, default=0)
    overall_score = Column(Float, nullable=True)         # 0.0 to 100.0
    duration_seconds = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Interview {self.id} status={self.status}>"