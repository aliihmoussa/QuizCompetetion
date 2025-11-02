"""
Scoring/Answer Data Access Layer
All database queries for student answer operations
"""
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database.models.student_ansawer import StudentAnswer
from database.base_data_access import BaseDataAccess


class ScoringDataAccess(BaseDataAccess):
    """
    Data access layer for StudentAnswer model.
    Handles all database operations for student answer entities.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize data access with database session

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
    
    # ==================== Answer CRUD Operations ====================
    
    def create_answer(
        self,
        session_id: Any,
        student_id: Any,
        question_id: Any,
        option_id: Any
    ) -> StudentAnswer:
        """Create a student answer"""
        answer = StudentAnswer(
            session_id=session_id,
            student_id=student_id,
            question_id=question_id,
            option_id=option_id
        )
        self.add(answer)
        self.commit()
        self.refresh(answer)
        return answer
    
    def get_answer_by_id(self, answer_id: Any) -> Optional[StudentAnswer]:
        """Get an answer by ID"""
        return self.db.query(StudentAnswer).filter(StudentAnswer.id == answer_id).first()
    
    def get_student_answer(
        self,
        session_id: Any,
        student_id: Any,
        question_id: Any
    ) -> Optional[StudentAnswer]:
        """Get a specific student's answer for a question"""
        return (self.db.query(StudentAnswer)
                .filter(StudentAnswer.session_id == session_id,
                       StudentAnswer.student_id == student_id,
                       StudentAnswer.question_id == question_id)
                .first())
    
    def submit_answer(
        self,
        session_id: Any,
        student_id: Any,
        question_id: Any,
        option_id: Any
    ) -> StudentAnswer:
        """Submit a student answer (create or update)"""
        # Check if answer already exists
        existing = self.get_student_answer(session_id, student_id, question_id)
        
        if existing:
            # Update existing answer
            existing.option_id = option_id
            existing.submitted_at = datetime.utcnow()
            self.commit()
            self.refresh(existing)
            return existing
        else:
            # Create new answer
            return self.create_answer(session_id, student_id, question_id, option_id)
    
    def delete_answer(self, answer_id: Any) -> bool:
        """Delete an answer"""
        answer = self.get_answer_by_id(answer_id)
        if answer:
            self.db.delete(answer)
            self.commit()
            return True
        return False
    
    # ==================== Answer Query Operations ====================
    
    def get_answers_by_session(self, session_id: Any) -> List[StudentAnswer]:
        """Get all answers for a session"""
        return (self.db.query(StudentAnswer)
                .filter(StudentAnswer.session_id == session_id)
                .all())
    
    def get_answers_by_student_and_session(
        self,
        session_id: Any,
        student_id: Any
    ) -> List[StudentAnswer]:
        """Get all answers by a student in a session"""
        return (self.db.query(StudentAnswer)
                .filter(StudentAnswer.session_id == session_id,
                       StudentAnswer.student_id == student_id)
                .all())
    
    def get_answers_by_question(self, question_id: Any) -> List[StudentAnswer]:
        """Get all answers for a specific question"""
        return (self.db.query(StudentAnswer)
                .filter(StudentAnswer.question_id == question_id)
                .all())
    
    # ==================== Answer Statistics Operations ====================
    
    def count_student_answers(self, session_id: Any, student_id: Any) -> int:
        """Count how many questions a student has answered in a session"""
        return (self.db.query(StudentAnswer)
                .filter(StudentAnswer.session_id == session_id,
                       StudentAnswer.student_id == student_id)
                .count())
    
    def count_answers_by_student(self, student_id: Any) -> int:
        """Count total answers by a student across all sessions"""
        return (self.db.query(func.count(StudentAnswer.id))
                .filter(StudentAnswer.student_id == student_id)
                .scalar() or 0)
    
    def count_answers_by_session(self, session_id: Any) -> int:
        """Count total answers in a session"""
        return (self.db.query(func.count(StudentAnswer.id))
                .filter(StudentAnswer.session_id == session_id)
                .scalar() or 0)
    
    def get_correct_answers_count(self, session_id: Any, student_id: Any) -> int:
        """Count correct answers by a student in a session"""
        return (self.db.query(func.count(StudentAnswer.id))
                .join(StudentAnswer.selected_option)
                .filter(StudentAnswer.session_id == session_id,
                       StudentAnswer.student_id == student_id,
                       StudentAnswer.selected_option.has(is_correct=True))
                .scalar() or 0)

