from sqlalchemy.ext.declarative import declarative_base

# Base model for all ORM models
Base = declarative_base()

# Import all models so Alembic and SQLAlchemy can discover them
from .user import User
from .quiz import Quiz
from .question import Question
from .question_option import QuestionOption
from .quiz_session import QuizSession
from .session_participiant import SessionParticipant
from .student_ansawer import StudentAnswer

# Import enums or shared constants (if defined here)
from database.enums import UserRole, SessionStatus

__all__ = [
    "Base",
    "User",
    "Quiz",
    "Question",
    "QuestionOption",
    "QuizSession",
    "SessionParticipant",
    "StudentAnswer",
    "UserRole",
    "SessionStatus",
]
