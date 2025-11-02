"""
Student/User Data Access Layer
All database queries for user and student operations
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database.models.user import User
from database.models.session_participiant import SessionParticipant
from database.models.student_ansawer import StudentAnswer
from database.models.quiz_session import QuizSession
from database.enums import UserRole
from database.base_data_access import BaseDataAccess


class StudentDataAccess(BaseDataAccess):
    """
    Data access layer for User model (students and instructors).
    Handles all database operations for user entities.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize data access with database session

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
    
    # ==================== User CRUD Operations ====================
    
    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole
    ) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        self.add(user)
        self.commit()
        self.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: Any) -> Optional[User]:
        """Get a user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def delete_user(self, user_id: Any) -> bool:
        """Delete a user"""
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.commit()
            return True
        return False
    
    # ==================== User Validation Operations ====================
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        return self.get_user_by_username(username) is not None
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.get_user_by_email(email) is not None
    
    # ==================== Student Query Operations ====================
    
    def get_students_by_ids(self, student_ids: List[Any]) -> List[User]:
        """Get multiple students by their IDs"""
        return (self.db.query(User)
                .filter(User.id.in_(student_ids), User.role == UserRole.STUDENT)
                .all())
    
    def get_all_students(self) -> List[User]:
        """Get all students"""
        return (self.db.query(User)
                .filter(User.role == UserRole.STUDENT)
                .order_by(User.created_at.desc())
                .all())
    
    # ==================== Student Statistics Operations ====================
    
    def get_student_count(self, instructor_id: Optional[Any] = None) -> int:
        """Get total count of students"""
        query = (self.db.query(func.count(func.distinct(User.id)))
                .filter(User.role == UserRole.STUDENT))
        
        if instructor_id:
            query = (query.join(SessionParticipant, User.id == SessionParticipant.student_id)
                    .join(QuizSession, SessionParticipant.session_id == QuizSession.id)
                    .filter(QuizSession.instructor_id == instructor_id))
        
        return query.scalar() or 0
    
    def get_all_students_with_stats(
        self,
        instructor_id: Optional[Any] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all students with their participation statistics"""
        # Build base query
        query = self.db.query(
            User.id,
            User.username,
            User.email,
            User.created_at,
            func.count(func.distinct(SessionParticipant.session_id)).label('total_sessions'),
            func.count(StudentAnswer.id).label('total_answers'),
            func.max(SessionParticipant.joined_at).label('last_active')
        ).filter(User.role == UserRole.STUDENT)
        
        # Join with session participants
        query = query.outerjoin(
            SessionParticipant,
            User.id == SessionParticipant.student_id
        )
        
        # Join with student answers
        query = query.outerjoin(
            StudentAnswer,
            User.id == StudentAnswer.student_id
        )
        
        # Filter by instructor if provided
        if instructor_id:
            query = (query.join(QuizSession, SessionParticipant.session_id == QuizSession.id)
                    .filter(QuizSession.instructor_id == instructor_id))
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_term)) |
                (User.email.ilike(search_term))
            )
        
        # Group by user
        query = query.group_by(User.id)
        
        # Order by last active (most recent first)
        query = query.order_by(desc('last_active'))
        
        # Pagination
        if limit:
            query = query.limit(limit).offset(offset)
        
        results = query.all()
        
        return [
            {
                'id': str(r.id),
                'username': r.username,
                'email': r.email,
                'created_at': r.created_at,
                'total_sessions': r.total_sessions or 0,
                'total_answers': r.total_answers or 0,
                'last_active': r.last_active
            }
            for r in results
        ]

