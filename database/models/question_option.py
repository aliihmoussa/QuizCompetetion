from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database import Base
class QuestionOption(Base):

    """Question option model"""
    __tablename__ = "question_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_text = Column(String(500), nullable=False)
    option_order = Column(Integer, nullable=False)  # A=1, B=2, C=3, D=4
    is_correct = Column(Boolean, default=False, nullable=False)

    # Relationships
    question = relationship("Question", back_populates="options")
    student_answers = relationship("StudentAnswer", back_populates="selected_option", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuestionOption(id={str(self.id)[:8]}..., order={self.option_order}, correct={self.is_correct})>"