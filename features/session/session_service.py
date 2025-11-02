"""
Session Service
Business logic for quiz session and participant management
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models.quiz_session import QuizSession
from database.models.session_participiant import SessionParticipant
from database.models import SessionStatus
from shared.session_code import generate_session_code
from .session_data_access import SessionDataAccess
from .participant_data_access import ParticipantDataAccess


class SessionService:
    """
    Service for session-related business logic.
    Handles validation, orchestration, and business rules.
    Uses separate data access layers for sessions and participants.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize service with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.session_data = SessionDataAccess(db_session)
        self.participant_data = ParticipantDataAccess(db_session)
    
    # ==================== Session Lifecycle Operations ====================
    
    def create_session(self, quiz_id: Any, instructor_id: Any) -> QuizSession:
        """
        Create a new quiz session with unique code
        
        Args:
            quiz_id: Quiz ID
            instructor_id: Instructor user ID
            
        Returns:
            Created QuizSession instance
        """
        # Generate unique session code
        session_code = generate_session_code(self.db)
        
        # Create session
        return self.session_data.create_session(quiz_id, instructor_id, session_code)
    
    def start_session(self, session_id: Any) -> dict:
        """
        Start a quiz session with validation
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary with 'success' boolean and 'message' or 'session'
        """
        session = self.session_data.get_session_by_id(session_id)
        
        if not session:
            return {'success': False, 'message': 'Session not found'}
        
        # Import here to avoid circular dependency
        from features.quiz import QuizDataAccess
        quiz_data = QuizDataAccess(self.db)
        
        # Get first question (need quiz data access)
        from features.quiz import QuestionDataAccess
        question_data = QuestionDataAccess(self.db)
        questions = question_data.get_questions_by_quiz(session.quiz_id)
        
        if not questions:
            return {'success': False, 'message': 'Quiz has no questions'}
        
        # Update session status
        self.session_data.update_status(session_id, SessionStatus.ACTIVE)
        
        # Set first question as current
        self.session_data.update_current_question(session_id, questions[0].id)
        
        # Refresh session
        self.db.refresh(session)
        
        return {'success': True, 'session': session}
    
    def end_session(self, session_id: Any) -> QuizSession:
        """
        End a quiz session
        
        Args:
            session_id: Session ID
            
        Returns:
            Updated QuizSession instance
        """
        return self.session_data.update_status(session_id, SessionStatus.CLOSED)
    
    def next_question(self, session_id: Any) -> dict:
        """
        Move to the next question in a session
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary with 'success' boolean and 'message' or 'question'
        """
        session = self.session_data.get_session_by_id(session_id)
        
        if not session:
            return {'success': False, 'message': 'Session not found'}
        
        # Get quiz questions
        from features.quiz import QuestionDataAccess
        question_data = QuestionDataAccess(self.db)
        questions = question_data.get_questions_by_quiz(session.quiz_id)
        
        # Find current question index
        current_idx = -1
        if session.current_question_id:
            for idx, q in enumerate(questions):
                if q.id == session.current_question_id:
                    current_idx = idx
                    break
        
        # Check if there's a next question
        next_idx = current_idx + 1
        if next_idx >= len(questions):
            return {'success': False, 'message': 'No more questions'}
        
        next_question = questions[next_idx]
        self.session_data.update_current_question(session_id, next_question.id)
        
        return {'success': True, 'question': next_question}
    
    # ==================== Session Query Operations ====================
    
    def get_session(self, session_id: Any) -> Optional[QuizSession]:
        """
        Get a session by ID
        
        Args:
            session_id: Session ID
            
        Returns:
            QuizSession instance or None
        """
        return self.session_data.get_session_by_id(session_id)
    
    def get_session_by_code(self, session_code: str) -> Optional[QuizSession]:
        """
        Get a session by code
        
        Args:
            session_code: Session code
            
        Returns:
            QuizSession instance or None
        """
        return self.session_data.get_session_by_code(session_code)
    
    def get_instructor_sessions(
        self,
        instructor_id: Any,
        status: Optional[SessionStatus] = None
    ) -> List[QuizSession]:
        """
        Get sessions by instructor
        
        Args:
            instructor_id: Instructor user ID
            status: Optional status filter
            
        Returns:
            List of QuizSession instances
        """
        return self.session_data.get_sessions_by_instructor(instructor_id, status)
    
    def get_recent_sessions(
        self,
        instructor_id: Any,
        limit: int = 5
    ) -> List[QuizSession]:
        """
        Get recent sessions by instructor
        
        Args:
            instructor_id: Instructor user ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of QuizSession instances ordered by creation date
        """
        return self.session_data.get_recent_sessions(instructor_id, limit)
    
    # ==================== Participant Operations ====================
    
    def join_session(self, session_code: str, student_id: Any) -> dict:
        """
        Join a student to a session with validation
        
        Args:
            session_code: Session code
            student_id: Student user ID
            
        Returns:
            Dictionary with 'success' boolean and 'message' or 'session'
        """
        session = self.session_data.get_session_by_code(session_code)
        
        if not session:
            return {'success': False, 'message': 'Invalid session code'}
        
        if session.status == SessionStatus.CLOSED:
            return {'success': False, 'message': 'This session has ended'}
        
        # Check if already a participant
        if self.participant_data.is_participant(session.id, student_id):
            return {'success': True, 'message': 'Already joined', 'session': session}
        
        # Add as participant
        self.participant_data.add_participant(session.id, student_id)
        
        return {'success': True, 'message': 'Joined successfully', 'session': session}
    
    def get_participants(self, session_id: Any) -> List[SessionParticipant]:
        """
        Get all participants in a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of SessionParticipant instances
        """
        return self.participant_data.get_participants_by_session(session_id)
    
    # ==================== Statistics Operations ====================
    
    def get_session_stats(self, instructor_id: Any) -> Dict[str, int]:
        """
        Get session statistics for an instructor
        
        Args:
            instructor_id: Instructor user ID
            
        Returns:
            Dictionary with session statistics
        """
        return self.session_data.get_session_stats(instructor_id)
    
    def get_active_sessions_count(self, instructor_id: Optional[Any] = None) -> int:
        """
        Get count of active sessions
        
        Args:
            instructor_id: Optional instructor filter
            
        Returns:
            Count of active sessions
        """
        return self.session_data.get_active_sessions_count(instructor_id)
    
    def get_active_sessions_with_details(self, instructor_id: Any) -> List[Dict[str, Any]]:
        """
        Get active sessions with details for dashboard
        
        Args:
            instructor_id: Instructor user ID
            
        Returns:
            List of active sessions with participant counts
        """
        return self.session_data.get_active_sessions_with_details(instructor_id)
    
    def get_total_participants_count(self, instructor_id: Any) -> int:
        """
        Get total unique participants across all instructor's sessions
        
        Args:
            instructor_id: Instructor user ID
            
        Returns:
            Total unique participant count
        """
        return self.participant_data.get_total_unique_participants(instructor_id)

