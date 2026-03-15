from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Response(Base):
    __tablename__ = "responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    audio_file_path = Column(String(500), nullable=True)     # Recorded audio
    transcribed_text = Column(Text, nullable=True)           # Whisper output
    transcription_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    duration_seconds = Column(Integer, nullable=True)
    status = Column(String(50), default="pending")           # pending, transcribed, evaluated
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    question = relationship("Question", back_populates="response")
    evaluation = relationship("Evaluation", back_populates="response", uselist=False)

    def __repr__(self):
        return f"<Response question={self.question_id} status={self.status}>"