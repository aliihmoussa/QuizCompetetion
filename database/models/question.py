
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from database import Base

class Question(Base):
    """Question model"""
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)
    time_limit = Column(Integer, default=30)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.option_order")
    student_answers = relationship("StudentAnswer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question(id={str(self.id)[:8]}..., order={self.question_order})>"