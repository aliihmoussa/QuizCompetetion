"""
Database Connection Management
Centralized singleton for database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import config


class DatabaseManager:
    """
    Singleton database manager for centralized connection handling.
    Ensures efficient connection pooling and proper resource management.
    """
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize database engine and session factory"""
        if self._initialized:
            return
        
        # Create engine with connection pooling
        self.engine = create_engine(
            config.DATABASE_URL,
            pool_pre_ping=True,      # Verify connections before using
            pool_size=10,            # Number of connections to maintain
            max_overflow=20,         # Max additional connections
            pool_recycle=3600,       # Recycle connections after 1 hour
            echo=False               # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        self._initialized = True
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions with automatic cleanup.
        
        Usage:
            with db_manager.get_session() as session:
                # Use session here
                user = session.query(User).first()
        
        The session will automatically commit on success or rollback on error.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session_simple(self) -> Session:
        """
        Get a database session (manual management required).
        
        Usage:
            db = db_manager.get_session_simple()
            try:
                # Use db here
            finally:
                db.close()
        
        Note: Prefer get_session() context manager when possible.
        """
        return self.SessionLocal()
    
    def dispose(self):
        """Dispose of the connection pool (useful for testing)"""
        if hasattr(self, 'engine'):
            self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Session:
    """
    Get a database session (backward compatibility).
    
    Usage:
        db = get_db()
        try:
            # Use db here
        finally:
            db.close()
    
    Returns:
        Session: SQLAlchemy database session
    """
    return db_manager.get_session_simple()


def get_db_context():
    """
    Get database session as context manager (recommended).
    
    Usage:
        with get_db_context() as db:
            # Use db here
    
    Returns:
        ContextManager[Session]: Database session context manager
    """
    return db_manager.get_session()

