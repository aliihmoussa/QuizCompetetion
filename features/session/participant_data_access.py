"""
Participant Data Access Layer
All database queries for session participant operations
"""
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models.session_participiant import SessionParticipant
from database.models.quiz_session import QuizSession
from database.base_data_access import BaseDataAccess


class ParticipantDataAccess(BaseDataAccess):
    """
    Data access layer for SessionParticipant model.
    Handles all database operations for session participant entities.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize data access with database session

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
    
    # ==================== Participant Operations ====================
    
    def add_participant(self, session_id: Any, student_id: Any) -> SessionParticipant:
        """Add a participant to a session"""
        participant = SessionParticipant(
            session_id=session_id,
            student_id=student_id
        )
        self.add(participant)
        self.commit()
        self.refresh(participant)
        return participant
    
    def get_participants_by_session(self, session_id: Any) -> List[SessionParticipant]:
        """Get all participants in a session"""
        return (self.db.query(SessionParticipant)
                .filter(SessionParticipant.session_id == session_id)
                .all())
    
    def get_participant(self, session_id: Any, student_id: Any) -> Optional[SessionParticipant]:
        """Get a specific participant"""
        return (self.db.query(SessionParticipant)
                .filter(SessionParticipant.session_id == session_id,
                       SessionParticipant.student_id == student_id)
                .first())
    
    def is_participant(self, session_id: Any, student_id: Any) -> bool:
        """Check if a student is a participant in a session"""
        return self.get_participant(session_id, student_id) is not None
    
    def get_participant_count(self, session_id: Any) -> int:
        """Get count of participants in a session"""
        return (self.db.query(func.count(SessionParticipant.id))
                .filter(SessionParticipant.session_id == session_id)
                .scalar() or 0)
    
    def remove_participant(self, session_id: Any, student_id: Any) -> bool:
        """Remove a participant from a session"""
        participant = self.get_participant(session_id, student_id)
        if participant:
            self.db.delete(participant)
            self.commit()
            return True
        return False
    
    # ==================== Participant Statistics ====================
    
    def get_total_unique_participants(self, instructor_id: Any) -> int:
        """Get total unique participants across all instructor's sessions"""
        count = (self.db.query(func.count(func.distinct(SessionParticipant.student_id)))
                .join(QuizSession, SessionParticipant.session_id == QuizSession.id)
                .filter(QuizSession.instructor_id == instructor_id)
                .scalar())
        
        return count or 0
    
    def get_sessions_for_student(self, student_id: Any) -> List[SessionParticipant]:
        """Get all session participations for a student"""
        return (self.db.query(SessionParticipant)
                .filter(SessionParticipant.student_id == student_id)
                .all())

