from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    parsed_text = Column(Text, nullable=True)
    extracted_skills = Column(JSONB, nullable=True)  # List of skills as JSON
    experience_years = Column(Integer, nullable=True)
    education = Column(JSONB, nullable=True)          # Education details as JSON
    work_experience = Column(JSONB, nullable=True)    # Work history as JSON
    is_parsed = Column(String(20), default="pending") # pending, processing, done, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    interviews = relationship("Interview", back_populates="resume")

    def __repr__(self):
        return f"<Resume {self.filename} for user {self.user_id}>"