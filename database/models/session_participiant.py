from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database import Base

class SessionParticipant(Base):
    """Session participant model - tracks which students joined which sessions"""
    __tablename__ = "session_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("QuizSession", back_populates="participants")
    student = relationship("User", back_populates="session_participations")

    def __repr__(self):
        return f"<SessionParticipant(session_id={str(self.session_id)[:8]}..., student_id={str(self.student_id)[:8]}...)>"