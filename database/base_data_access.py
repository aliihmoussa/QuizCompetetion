"""
Base Data Access Layer
Provides common database operations for all feature-specific data access classes
"""
from sqlalchemy.orm import Session
from typing import Any, TypeVar, Generic

T = TypeVar('T')


class BaseDataAccess(Generic[T]):
    """
    Base class for all data access layers.
    Centralizes common database operations to ensure consistency
    and reduce code duplication across feature modules.
    """

    def __init__(self, db_session: Session):
        """
        Initialize data access with database session

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    # ==================== Core Database Operations ====================

    def add(self, model: T) -> T:
        """
        Add a model instance to the session

        Args:
            model: SQLAlchemy model instance

        Returns:
            The same model instance
        """
        self.db.add(model)
        return model

    def flush(self) -> None:
        """
        Flush pending changes to the database without committing
        """
        self.db.flush()

    def commit(self) -> None:
        """
        Commit the current transaction
        """
        self.db.commit()

    def rollback(self) -> None:
        """
        Rollback the current transaction
        """
        self.db.rollback()

    def close(self) -> None:
        """
        Close the database session
        """
        self.db.close()

    def refresh(self, model: T) -> None:
        """
        Refresh a model instance from the database

        Args:
            model: SQLAlchemy model instance
        """
        self.db.refresh(model)

    def delete(self, model: T) -> None:
        """
        Delete a model instance from the database

        Args:
            model: SQLAlchemy model instance
        """
        self.db.delete(model)

    def add_all(self, models: list[T]) -> None:
        """
        Add multiple model instances to the session

        Args:
            models: List of SQLAlchemy model instances
        """
        self.db.add_all(models)

    def expunge(self, model: T) -> None:
        """
        Remove a model instance from the session

        Args:
            model: SQLAlchemy model instance
        """
        self.db.expunge(model)

    def expunge_all(self) -> None:
        """
        Remove all model instances from the session
        """
        self.db.expunge_all()

