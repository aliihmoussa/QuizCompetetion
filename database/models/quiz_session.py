
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.enums import SessionStatus
from database import Base
class QuizSession(Base):
    """Quiz session model"""
    __tablename__ = "quiz_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_code = Column(String(10), unique=True, nullable=False, index=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.PENDING, nullable=False)
    current_question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    quiz = relationship("Quiz", back_populates="sessions")
    instructor = relationship("User", back_populates="quiz_sessions")
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")
    student_answers = relationship("StudentAnswer", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuizSession(id={str(self.id)[:8]}..., code='{self.session_code}', status='{self.status.value}')>"