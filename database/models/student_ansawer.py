from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base
class StudentAnswer(Base):
    """Student answer model - tracks all answers submitted"""
    __tablename__ = "student_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_id = Column(UUID(as_uuid=True), ForeignKey("question_options.id", ondelete="SET NULL"), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("QuizSession", back_populates="student_answers")
    student = relationship("User", back_populates="student_answers")
    question = relationship("Question", back_populates="student_answers")
    selected_option = relationship("QuestionOption", back_populates="student_answers")

    def __repr__(self):
        return f"<StudentAnswer(id={str(self.id)[:8]}..., student_id={str(self.student_id)[:8]}..., question_id={str(self.question_id)[:8]}...)>"