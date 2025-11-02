"""
Quiz Data Access Layer
All database queries for quiz-related operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database.models.quiz import Quiz
from database.models.question import Question
from database.models.quiz_session import QuizSession
from database.base_data_access import BaseDataAccess


class QuizDataAccess(BaseDataAccess):
    """
    Data access layer for Quiz model.
    Handles all database operations for quiz entities.
    Note: Question-related operations are in question_data_access.py
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize data access with database session

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
    
    # ==================== Quiz Operations ====================
    
    def create_quiz(self, instructor_id: Any, title: str, description: str = None) -> Quiz:
        """Create a new quiz"""
        quiz = Quiz(
            instructor_id=instructor_id,
            title=title,
            description=description
        )
        self.add(quiz)
        self.commit()
        self.refresh(quiz)
        return quiz
    
    def get_quiz_by_id(self, quiz_id: Any) -> Optional[Quiz]:
        """Get a quiz by ID"""
        return self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    def get_quizzes_by_instructor(self, instructor_id: Any) -> List[Quiz]:
        """Get all quizzes created by an instructor"""
        return (self.db.query(Quiz)
                .filter(Quiz.instructor_id == instructor_id)
                .order_by(desc(Quiz.created_at))
                .all())
    
    def update_quiz(self, quiz_id: Any, title: str = None, description: str = None) -> Optional[Quiz]:
        """Update a quiz's metadata"""
        quiz = self.get_quiz_by_id(quiz_id)
        if quiz:
            if title is not None:
                quiz.title = title
            if description is not None:
                quiz.description = description
            self.commit()
            self.refresh(quiz)
        return quiz
    
    def delete_quiz(self, quiz_id: Any) -> bool:
        """Delete a quiz (cascades to questions)"""
        quiz = self.get_quiz_by_id(quiz_id)
        if quiz:
            self.delete(quiz)
            self.commit()
            return True
        return False
    
    def get_quiz_count(self, instructor_id: Any) -> int:
        """Get total count of quizzes for an instructor"""
        return (self.db.query(func.count(Quiz.id))
                .filter(Quiz.instructor_id == instructor_id)
                .scalar() or 0)
    
    def get_quiz_stats(self, instructor_id: Any) -> Dict[str, Any]:
        """Get quiz statistics for an instructor"""
        total_quizzes = self.get_quiz_count(instructor_id)
        
        # Get total questions across all quizzes
        total_questions = (self.db.query(func.count(Question.id))
                          .join(Quiz, Question.quiz_id == Quiz.id)
                          .filter(Quiz.instructor_id == instructor_id)
                          .scalar() or 0)
        
        # Get total sessions across all quizzes
        total_sessions = (self.db.query(func.count(QuizSession.id))
                         .join(Quiz, QuizSession.quiz_id == Quiz.id)
                         .filter(Quiz.instructor_id == instructor_id)
                         .scalar() or 0)
        
        return {
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'total_sessions': total_sessions,
            'avg_questions_per_quiz': total_questions / total_quizzes if total_quizzes > 0 else 0
        }
    

