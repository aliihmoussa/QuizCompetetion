"""
Quiz Service
Business logic for quiz and question management
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models.quiz import Quiz
from database.models.question import Question
from .quiz_data_access import QuizDataAccess
from .question_data_access import QuestionDataAccess


class QuizService:
    """
    Service for quiz-related business logic.
    Handles validation, orchestration, and business rules.
    Uses separate data access layers for quizzes and questions.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize service with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.quiz_data = QuizDataAccess(db_session)
        self.question_data = QuestionDataAccess(db_session)
    
    # ==================== Quiz Operations ====================
    
    def create_quiz(self, instructor_id: Any, title: str, description: str = None) -> Quiz:
        """
        Create a new quiz with validation
        
        Args:
            instructor_id: Creator's user ID
            title: Quiz title
            description: Optional description
            
        Returns:
            Created Quiz instance
            
        Raises:
            ValueError: If title is invalid
        """
        if not title or len(title.strip()) < 3:
            raise ValueError("Quiz title must be at least 3 characters")
        
        return self.quiz_data.create_quiz(instructor_id, title.strip(), description)
    
    def get_quiz(self, quiz_id: Any) -> Optional[Quiz]:
        """
        Get a quiz by ID
        
        Args:
            quiz_id: Quiz ID
            
        Returns:
            Quiz instance or None
        """
        return self.quiz_data.get_quiz_by_id(quiz_id)
    
    def get_instructor_quizzes(self, instructor_id: Any) -> List[Quiz]:
        """
        Get all quizzes by an instructor
        
        Args:
            instructor_id: Instructor user ID
            
        Returns:
            List of Quiz instances ordered by creation date (newest first)
        """
        return self.quiz_data.get_quizzes_by_instructor(instructor_id)
    
    def update_quiz(self, quiz_id: Any, title: str = None, description: str = None) -> Optional[Quiz]:
        """
        Update a quiz's metadata
        
        Args:
            quiz_id: Quiz ID
            title: New title (optional)
            description: New description (optional)
            
        Returns:
            Updated Quiz instance or None
            
        Raises:
            ValueError: If title is invalid
        """
        if title is not None and len(title.strip()) < 3:
            raise ValueError("Quiz title must be at least 3 characters")
        
        return self.quiz_data.update_quiz(
            quiz_id,
            title.strip() if title else None,
            description
        )
    
    def delete_quiz(self, quiz_id: Any) -> bool:
        """
        Delete a quiz
        
        Args:
            quiz_id: Quiz ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.quiz_data.delete_quiz(quiz_id)
    
    def get_quiz_stats(self, instructor_id: Any) -> Dict[str, Any]:
        """
        Get comprehensive quiz statistics for an instructor
        
        Args:
            instructor_id: Instructor user ID
            
        Returns:
            Dictionary with quiz statistics
        """
        return self.quiz_data.get_quiz_stats(instructor_id)
    
    def get_quiz_count(self, instructor_id: Any) -> int:
        """
        Get total quiz count for an instructor
        
        Args:
            instructor_id: Instructor user ID
            
        Returns:
            Total quiz count
        """
        return self.quiz_data.get_quiz_count(instructor_id)
    
    # ==================== Question Operations ====================
    
    def get_quiz_questions(self, quiz_id: Any) -> List[Question]:
        """
        Get all questions for a quiz
        
        Args:
            quiz_id: Quiz ID
            
        Returns:
            List of Question instances ordered by question_order
        """
        return self.question_data.get_questions_by_quiz(quiz_id)
    
    def get_question(self, question_id: Any) -> Optional[Question]:
        """
        Get a question by ID
        
        Args:
            question_id: Question ID
            
        Returns:
            Question instance or None
        """
        return self.question_data.get_question_by_id(question_id)
    
    def add_question(
        self,
        quiz_id: Any,
        question_text: str,
        question_order: int,
        options: List[dict],
        time_limit: int = 30
    ) -> Question:
        """
        Add a question to a quiz with its options
        
        Args:
            quiz_id: Quiz ID
            question_text: Question text
            question_order: Order/position of question
            options: List of dicts with 'text', 'order', 'is_correct'
            time_limit: Time limit in seconds
            
        Returns:
            Created Question instance
            
        Raises:
            ValueError: If validation fails
        """
        # Validate question text
        if not question_text or len(question_text.strip()) < 5:
            raise ValueError("Question text must be at least 5 characters")
        
        # Validate options
        if not options or len(options) < 2:
            raise ValueError("Question must have at least 2 options")
        
        if not any(opt.get('is_correct', False) for opt in options):
            raise ValueError("Question must have at least one correct answer")
        
        # Create question
        question = self.question_data.create_question(
            quiz_id,
            question_text.strip(),
            question_order,
            time_limit
        )
        
        # Create options
        for option in options:
            self.question_data.create_question_option(
                question.id,
                option['text'],
                option['order'],
                option.get('is_correct', False)
            )
        
        # Refresh to get options
        self.db.refresh(question)
        return question
    
    def update_question(
        self,
        question_id: Any,
        question_text: str,
        options: List[dict],
        time_limit: int = 30
    ) -> Optional[Question]:
        """
        Update a question and its options
        
        Args:
            question_id: Question ID
            question_text: Updated question text
            options: List of dicts with 'text', 'order', 'is_correct'
            time_limit: Time limit in seconds
            
        Returns:
            Updated Question instance or None
            
        Raises:
            ValueError: If validation fails
        """
        # Validate question text
        if not question_text or len(question_text.strip()) < 5:
            raise ValueError("Question text must be at least 5 characters")
        
        # Validate options
        if not options or len(options) < 2:
            raise ValueError("Question must have at least 2 options")
        
        if not any(opt.get('is_correct', False) for opt in options):
            raise ValueError("Question must have at least one correct answer")
        
        # Update question
        question = self.question_data.update_question(
            question_id,
            question_text.strip(),
            time_limit
        )
        
        if not question:
            return None
        
        # Delete old options
        self.question_data.delete_question_options(question_id)
        
        # Create new options
        for option in options:
            self.question_data.create_question_option(
                question.id,
                option['text'],
                option['order'],
                option.get('is_correct', False)
            )
        
        # Refresh to get new options
        self.db.refresh(question)
        return question
    
    def validate_quiz_completeness(self, quiz_id: Any) -> dict:
        """
        Validate that a quiz is complete and ready to be used
        
        Args:
            quiz_id: Quiz ID
            
        Returns:
            Dictionary with 'valid' boolean and 'message' if invalid
        """
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            return {'valid': False, 'message': 'Quiz not found'}
        
        questions = self.get_quiz_questions(quiz_id)
        if not questions:
            return {'valid': False, 'message': 'Quiz has no questions'}
        
        # Check each question has options
        for question in questions:
            if not question.options or len(question.options) == 0:
                return {
                    'valid': False,
                    'message': f'Question {question.question_order} has no options'
                }
            
            # Check at least one correct answer
            if not any(opt.is_correct for opt in question.options):
                return {
                    'valid': False,
                    'message': f'Question {question.question_order} has no correct answer'
                }
        
        return {'valid': True}

