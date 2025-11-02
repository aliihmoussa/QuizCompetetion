
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.enums import UserRole
from database import Base

class User(Base):
    """User model for both instructors and students"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    created_quizzes = relationship("Quiz", back_populates="instructor", cascade="all, delete-orphan")
    quiz_sessions = relationship("QuizSession", back_populates="instructor", cascade="all, delete-orphan")
    session_participations = relationship("SessionParticipant", back_populates="student", cascade="all, delete-orphan")
    student_answers = relationship("StudentAnswer", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={str(self.id)[:8]}..., username='{self.username}', role='{self.role.value}')>"