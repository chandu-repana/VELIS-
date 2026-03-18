from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class InterviewStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Interview(Base, TimestampMixin):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False, default="Interview Session")
    job_role = Column(String(100), nullable=True)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.PENDING, nullable=False)
    overall_score = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    total_questions = Column(Integer, default=0)
    answered_questions = Column(Integer, default=0)

    user = relationship("User", backref="interviews")
    resume = relationship("Resume", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Interview id={self.id} status={self.status}>"
