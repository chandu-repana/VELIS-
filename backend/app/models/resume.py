from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    raw_text = Column(Text, nullable=True)
    extracted_skills = Column(JSON, default=list)
    experience_years = Column(Integer, default=0)
    education = Column(JSON, default=list)
    is_parsed = Column(Boolean, default=False, nullable=False)

    user = relationship("User", backref="resumes")
    interviews = relationship("Interview", back_populates="resume")

    def __repr__(self):
        return f"<Resume id={self.id} user_id={self.user_id}>"
