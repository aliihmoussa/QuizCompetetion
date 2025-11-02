"""
Database package initialization
Centralized database connection and model management
"""
from sqlalchemy.orm import declarative_base

# Import centralized connection management
from database.connection import (
    db_manager,
    get_db,
    get_db_context,
    DatabaseManager
)

# ----------------------------------------
# Declarative base for all ORM models
# ----------------------------------------
Base = declarative_base()

# ----------------------------------------
# Legacy exports for backward compatibility
# ----------------------------------------
# Access engine and SessionLocal through db_manager
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal


# ----------------------------------------
# Database initialization
# ----------------------------------------
def init_db():
    """
    Initialize the database by creating all tables.
    Imports all model definitions before calling create_all()
    so SQLAlchemy knows about them.
    """
    # Import models here so they are registered properly
    from database.models import (
        User,
        Quiz,
        Question,
        QuestionOption,
        QuizSession,
        SessionParticipant,
        StudentAnswer
    )

    # Use centralized database manager
    Base.metadata.create_all(bind=db_manager.engine)


# ----------------------------------------
# Public API exports
# ----------------------------------------
__all__ = [
    'Base',
    'db_manager',
    'get_db',
    'get_db_context',
    'init_db',
    'engine',
    'SessionLocal',
    'DatabaseManager'
]
