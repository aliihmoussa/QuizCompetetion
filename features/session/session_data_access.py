"""
Session Data Access Layer
All database queries for quiz session operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from database.models.quiz_session import QuizSession
from database.models.session_participiant import SessionParticipant
from database.models.quiz import Quiz
from database.models import SessionStatus
from database.base_data_access import BaseDataAccess


class SessionDataAccess(BaseDataAccess):
    """
    Data access layer for QuizSession model.
    Handles all database operations for quiz session entities.
    Note: Participant operations are in participant_data_access.py
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize data access with database session

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
    
    # ==================== Session CRUD Operations ====================
    
    def create_session(
        self,
        quiz_id: Any,
        instructor_id: Any,
        session_code: str
    ) -> QuizSession:
        """Create a new quiz session"""
        session = QuizSession(
            quiz_id=quiz_id,
            instructor_id=instructor_id,
            session_code=session_code,
            status=SessionStatus.PENDING
        )
        self.add(session)
        self.commit()
        self.refresh(session)
        return session
    
    def get_session_by_id(self, session_id: Any) -> Optional[QuizSession]:
        """Get a session by ID"""
        return self.db.query(QuizSession).filter(QuizSession.id == session_id).first()
    
    def get_session_by_code(self, session_code: str) -> Optional[QuizSession]:
        """Get session by session code"""
        return (self.db.query(QuizSession)
                .filter(QuizSession.session_code == session_code)
                .first())
    
    def delete_session(self, session_id: Any) -> bool:
        """Delete a session"""
        session = self.get_session_by_id(session_id)
        if session:
            self.delete(session)
            self.commit()
            return True
        return False
    
    # ==================== Session Status Operations ====================
    
    def update_status(self, session_id: Any, status: SessionStatus) -> Optional[QuizSession]:
        """Update session status with automatic timestamp management"""
        session = self.get_session_by_id(session_id)
        print("ana_honnnnnn")
        print(session)
        if session:
            session.status = status
            
            # Set timestamps based on status
            if status == SessionStatus.ACTIVE and not session.start_time:
                session.start_time = datetime.utcnow()
            elif status == SessionStatus.CLOSED and not session.end_time:
                session.end_time = datetime.utcnow()
            
            self.commit()
            self.refresh(session)
        return session
    
    def update_current_question(
        self,
        session_id: Any,
        question_id: Any
    ) -> Optional[QuizSession]:
        """Update the current question for a session"""
        session = self.get_session_by_id(session_id)
        if session:
            session.current_question_id = question_id
            self.commit()
            self.refresh(session)
        return session
    
    # ==================== Session Queries ====================
    
    def get_sessions_by_instructor(
        self,
        instructor_id: Any,
        status: Optional[SessionStatus] = None
    ) -> List[QuizSession]:
        """Get sessions by instructor, optionally filtered by status"""
        query = (self.db.query(QuizSession)
                .filter(QuizSession.instructor_id == instructor_id))
        
        if status:
            query = query.filter(QuizSession.status == status)
        
        return query.order_by(desc(QuizSession.created_at)).all()
    
    def get_recent_sessions(
        self,
        instructor_id: Any,
        limit: int = 5
    ) -> List[QuizSession]:
        """Get recent sessions by instructor, ordered by creation date"""
        return (self.db.query(QuizSession)
                .filter(QuizSession.instructor_id == instructor_id)
                .order_by(desc(QuizSession.created_at))
                .limit(limit)
                .all())
    
    def session_code_exists(self, session_code: str) -> bool:
        """Check if a session code already exists"""
        return self.get_session_by_code(session_code) is not None
    
    # ==================== Session Statistics ====================
    
    def get_active_sessions_count(self, instructor_id: Optional[Any] = None) -> int:
        """Get count of active sessions"""
        query = self.db.query(func.count(QuizSession.id)).filter(
            QuizSession.status == SessionStatus.ACTIVE
        )
        
        if instructor_id:
            query = query.filter(QuizSession.instructor_id == instructor_id)
        
        return query.scalar() or 0
    
    def get_session_stats(self, instructor_id: Any) -> Dict[str, int]:
        """Get session statistics for an instructor"""
        total = (self.db.query(func.count(QuizSession.id))
                .filter(QuizSession.instructor_id == instructor_id)
                .scalar() or 0)
        
        active = (self.db.query(func.count(QuizSession.id))
                 .filter(QuizSession.instructor_id == instructor_id,
                        QuizSession.status == SessionStatus.ACTIVE)
                 .scalar() or 0)
        
        closed = (self.db.query(func.count(QuizSession.id))
                 .filter(QuizSession.instructor_id == instructor_id,
                        QuizSession.status == SessionStatus.CLOSED)
                 .scalar() or 0)
        
        pending = (self.db.query(func.count(QuizSession.id))
                  .filter(QuizSession.instructor_id == instructor_id,
                         QuizSession.status == SessionStatus.PENDING)
                  .scalar() or 0)
        
        return {
            'total': total,
            'active': active,
            'closed': closed,
            'pending': pending
        }
    
    def get_active_sessions_with_details(self, instructor_id: Any) -> List[Dict[str, Any]]:
        """Get active sessions with participant counts and quiz details"""
        results = self.db.query(
            QuizSession,
            func.count(SessionParticipant.id).label('participant_count')
        ).join(
            Quiz,
            QuizSession.quiz_id == Quiz.id
        ).outerjoin(
            SessionParticipant,
            QuizSession.id == SessionParticipant.session_id
        ).filter(
            QuizSession.instructor_id == instructor_id,
            QuizSession.status == SessionStatus.ACTIVE
        ).group_by(QuizSession.id, Quiz.id).all()
        
        return [
            {
                'session': session,
                'participant_count': count,
                'quiz_title': session.quiz.title
            }
            for session, count in results
        ]

