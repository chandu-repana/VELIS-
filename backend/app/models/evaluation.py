from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = Column(UUID(as_uuid=True), ForeignKey("responses.id"), nullable=False)
    overall_score = Column(Float, nullable=True)          # 0.0 to 100.0
    relevance_score = Column(Float, nullable=True)        # How relevant the answer was
    clarity_score = Column(Float, nullable=True)          # How clearly explained
    depth_score = Column(Float, nullable=True)            # Technical depth
    feedback_text = Column(Text, nullable=True)           # AI-generated feedback
    strengths = Column(JSONB, nullable=True)              # List of strong points
    improvements = Column(JSONB, nullable=True)           # List of areas to improve
    ideal_answer_hint = Column(Text, nullable=True)       # What a good answer looks like
    evaluated_by = Column(String(100), default="llm")     # llm or human
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    response = relationship("Response", back_populates="evaluation")

    def __repr__(self):
        return f"<Evaluation score={self.overall_score}>"