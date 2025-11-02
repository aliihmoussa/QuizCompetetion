"""
Question Data Access Layer
All database queries for question and question option operations
"""
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models.question import Question
from database.models.question_option import QuestionOption
from database.base_data_access import BaseDataAccess


class QuestionDataAccess(BaseDataAccess):
    """
    Data access layer for Question and QuestionOption models.
    Handles all database operations for question-related entities.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize data access with database session

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
    
    # ==================== Question Operations ====================
    
    def get_questions_by_quiz(self, quiz_id: Any) -> List[Question]:
        """Get all questions for a quiz, ordered by question_order"""
        return (self.db.query(Question)
                .filter(Question.quiz_id == quiz_id)
                .order_by(Question.question_order)
                .all())
    
    def get_question_by_id(self, question_id: Any) -> Optional[Question]:
        """Get a question by ID"""
        return self.db.query(Question).filter(Question.id == question_id).first()
    
    def create_question(
        self,
        quiz_id: Any,
        question_text: str,
        question_order: int,
        time_limit: int = 30
    ) -> Question:
        """Create a new question"""
        question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            question_order=question_order,
            time_limit=time_limit
        )
        self.add(question)
        self.commit()
        self.refresh(question)
        return question
    
    def update_question(
        self,
        question_id: Any,
        question_text: str = None,
        time_limit: int = None
    ) -> Optional[Question]:
        """Update a question"""
        question = self.get_question_by_id(question_id)
        if question:
            if question_text is not None:
                question.question_text = question_text
            if time_limit is not None:
                question.time_limit = time_limit
            self.commit()
            self.refresh(question)
        return question
    
    def delete_question(self, question_id: Any) -> bool:
        """Delete a question"""
        question = self.get_question_by_id(question_id)
        if question:
            self.delete(question)
            self.commit()
            return True
        return False
    
    def get_question_count_by_quiz(self, quiz_id: Any) -> int:
        """Get number of questions in a quiz"""
        return (self.db.query(func.count(Question.id))
                .filter(Question.quiz_id == quiz_id)
                .scalar() or 0)
    
    # ==================== Question Option Operations ====================
    
    def create_question_option(
        self,
        question_id: Any,
        option_text: str,
        option_order: int,
        is_correct: bool = False
    ) -> QuestionOption:
        """Create a question option"""
        option = QuestionOption(
            question_id=question_id,
            option_text=option_text,
            option_order=option_order,
            is_correct=is_correct
        )
        self.add(option)
        self.commit()
        self.refresh(option)
        return option
    
    def get_option_by_id(self, option_id: Any) -> Optional[QuestionOption]:
        """Get an option by ID"""
        return self.db.query(QuestionOption).filter(QuestionOption.id == option_id).first()
    
    def get_options_by_question(self, question_id: Any) -> List[QuestionOption]:
        """Get all options for a question, ordered by option_order"""
        return (self.db.query(QuestionOption)
                .filter(QuestionOption.question_id == question_id)
                .order_by(QuestionOption.option_order)
                .all())
    
    def update_question_option(
        self,
        option_id: Any,
        option_text: str = None,
        is_correct: bool = None
    ) -> Optional[QuestionOption]:
        """Update a question option"""
        option = self.get_option_by_id(option_id)
        if option:
            if option_text is not None:
                option.option_text = option_text
            if is_correct is not None:
                option.is_correct = is_correct
            self.commit()
            self.refresh(option)
        return option
    
    def delete_question_options(self, question_id: Any) -> bool:
        """Delete all options for a question"""
        self.db.query(QuestionOption).filter(QuestionOption.question_id == question_id).delete()
        self.commit()
        return True
    
    def delete_option_by_id(self, option_id: Any) -> bool:
        """Delete a specific option by ID"""
        option = self.get_option_by_id(option_id)
        if option:
            self.delete(option)
            self.commit()
            return True
        return False
    
    def get_correct_option(self, question_id: Any) -> Optional[QuestionOption]:
        """Get the correct option for a question"""
        return (self.db.query(QuestionOption)
                .filter(QuestionOption.question_id == question_id)
                .filter(QuestionOption.is_correct == True)
                .first())
    
    def has_correct_answer(self, question_id: Any) -> bool:
        """Check if a question has at least one correct answer"""
        count = (self.db.query(func.count(QuestionOption.id))
                .filter(QuestionOption.question_id == question_id)
                .filter(QuestionOption.is_correct == True)
                .scalar() or 0)
        return count > 0

