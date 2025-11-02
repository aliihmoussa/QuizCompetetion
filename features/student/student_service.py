"""
Student Service
Business logic for student/user management operations
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from database.models.user import User
from database.enums import UserRole
from shared.auth_helpers import hash_password, verify_password
from .student_data_access import StudentDataAccess


class StudentService:
    """
    Service for student and user-related business logic.
    Handles validation, orchestration, and business rules.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize service with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.data_access = StudentDataAccess(db_session)
    
    # ==================== Authentication Operations ====================
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User instance if authentication successful, None otherwise
        """
        user = self.data_access.get_user_by_username(username)
        
        if not user:
            return None
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole
    ) -> dict:
        """
        Register a new user with validation
        
        Args:
            username: Desired username
            email: Email address
            password: Plain text password
            role: User role
            
        Returns:
            Dictionary with 'success' boolean and 'message' or 'user'
        """
        # Validation
        if len(username.strip()) < 3:
            return {
                'success': False,
                'message': 'Username must be at least 3 characters long'
            }
        
        if len(password) < 6:
            return {
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }
        
        # Check if username exists
        if self.data_access.username_exists(username):
            return {
                'success': False,
                'message': 'Username already exists'
            }
        
        # Check if email exists
        if self.data_access.email_exists(email):
            return {
                'success': False,
                'message': 'Email already exists'
            }
        
        # Hash password and create user
        password_hash = hash_password(password)
        user = self.data_access.create_user(username.strip(), email, password_hash, role)
        
        return {
            'success': True,
            'user': user
        }
    
    # ==================== User Query Operations ====================
    
    def get_user_by_id(self, user_id: Any) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User instance or None
        """
        return self.data_access.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User instance or None
        """
        return self.data_access.get_user_by_username(username)
    
    # ==================== Student Operations ====================
    
    def get_all_students(self) -> List[User]:
        """
        Get all students
        
        Returns:
            List of User instances with STUDENT role
        """
        return self.data_access.get_all_students()
    
    def get_students_by_ids(self, student_ids: List[Any]) -> List[User]:
        """
        Get multiple students by their IDs
        
        Args:
            student_ids: List of student IDs
            
        Returns:
            List of User instances
        """
        return self.data_access.get_students_by_ids(student_ids)
    
    def get_student_count(self, instructor_id: Optional[Any] = None) -> int:
        """
        Get total count of students
        
        Args:
            instructor_id: Optional filter by instructor's sessions
            
        Returns:
            Total count of students
        """
        return self.data_access.get_student_count(instructor_id)
    
    def get_all_students_with_stats(
        self,
        instructor_id: Optional[Any] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all students with their participation statistics
        
        Args:
            instructor_id: Optional filter by instructor's sessions
            search: Optional search by username or email
            limit: Optional limit number of results
            offset: Offset for pagination
            
        Returns:
            List of dictionaries with student stats
        """
        return self.data_access.get_all_students_with_stats(
            instructor_id,
            search,
            limit,
            offset
        )

