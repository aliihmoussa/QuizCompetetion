"""
Scoring Service
Business logic for scoring, leaderboard calculations, and answer management
"""
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime
from database.models.quiz_session import QuizSession
from database.models.student_ansawer import StudentAnswer
from config import BASE_POINTS, SPEED_PENALTY_MULTIPLIER
from .scoring_data_access import ScoringDataAccess


class ScoringService:
    """
    Service for scoring and leaderboard business logic.
    Handles answer submission, score calculation, and leaderboard generation.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize service with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.data_access = ScoringDataAccess(db_session)
    
    # ==================== Answer Submission Operations ====================
    
    def submit_answer(
        self,
        session_id: Any,
        student_id: Any,
        question_id: Any,
        option_id: Any
    ) -> StudentAnswer:
        """
        Submit a student answer
        
        Args:
            session_id: Session ID
            student_id: Student user ID
            question_id: Question ID
            option_id: Selected option ID
            
        Returns:
            Created/Updated StudentAnswer instance
        """
        return self.data_access.submit_answer(
            session_id,
            student_id,
            question_id,
            option_id
        )
    
    def get_student_answer(
        self,
        session_id: Any,
        student_id: Any,
        question_id: Any
    ) -> Optional[StudentAnswer]:
        """Get a specific student's answer for a question"""
        return self.data_access.get_student_answer(session_id, student_id, question_id)
    
    def get_student_answers(
        self,
        session_id: Any,
        student_id: Any
    ) -> List[StudentAnswer]:
        """Get all answers by a student in a session"""
        return self.data_access.get_answers_by_student_and_session(session_id, student_id)
    
    def count_student_answers(self, session_id: Any, student_id: Any) -> int:
        """Count how many questions a student has answered"""
        return self.data_access.count_student_answers(session_id, student_id)
    
    def count_total_answers_by_student(self, student_id: Any) -> int:
        """Count total answers by a student across all sessions"""
        return self.data_access.count_answers_by_student(student_id)
    
    # ==================== Scoring Calculations ====================
    
    def calculate_answer_score(
        self,
        answer: StudentAnswer,
        question_start_time: datetime,
        time_limit: int
    ) -> int:
        """
        Calculate score for a single answer based on correctness and speed
        
        Args:
            answer: StudentAnswer object
            question_start_time: When the question was presented
            time_limit: Question time limit in seconds
            
        Returns:
            Score points (0 if incorrect, BASE_POINTS - speed_penalty if correct)
        """
        # Check if answer is correct
        if not answer.selected_option or not answer.selected_option.is_correct:
            return 0
        
        # Calculate time taken in seconds
        time_taken = (answer.submitted_at - question_start_time).total_seconds()
        time_taken = max(0, min(time_taken, time_limit))  # Clamp between 0 and time_limit
        
        # Calculate speed penalty
        speed_penalty = int((time_taken / time_limit) * BASE_POINTS * SPEED_PENALTY_MULTIPLIER)
        
        # Final score
        score = BASE_POINTS - speed_penalty
        return max(0, score)  # Ensure non-negative
    
    def calculate_leaderboard(self, session: QuizSession) -> List[Dict]:
        """
        Calculate leaderboard for a quiz session
        
        Args:
            session: QuizSession object
            
        Returns:
            List of leaderboard entries sorted by score (descending)
        """
        # Import here to avoid circular dependency
        from features.session import ParticipantDataAccess
        from features.quiz import QuestionDataAccess
        
        participant_data = ParticipantDataAccess(self.db)
        question_data = QuestionDataAccess(self.db)
        
        # Get all participants
        participants = participant_data.get_participants_by_session(session.id)
        
        # Get all questions for this quiz
        questions = question_data.get_questions_by_quiz(session.quiz_id)
        total_questions = len(questions)
        
        if total_questions == 0:
            return []
        
        # Get all answers for this session
        all_answers = self.data_access.get_answers_by_session(session.id)
        
        # Group answers by student
        student_scores = {}
        for participant in participants:
            student_id = participant.student_id
            student = participant.student
            
            # Get student's answers
            student_answers = [a for a in all_answers if a.student_id == student_id]
            
            total_points = 0
            correct_count = 0
            
            for answer in student_answers:
                # Use session start time as question start time
                question_start_time = session.start_time or session.created_at
                
                score = self.calculate_answer_score(
                    answer,
                    question_start_time,
                    answer.question.time_limit
                )
                total_points += score
                
                if answer.selected_option and answer.selected_option.is_correct:
                    correct_count += 1
            
            answered_count = len(student_answers)
            percent_correct = (correct_count / answered_count * 100) if answered_count > 0 else 0
            
            student_scores[student_id] = {
                'student_id': student_id,
                'student_name': student.username,
                'total_points': total_points,
                'correct_count': correct_count,
                'total_questions': total_questions,
                'answered_count': answered_count,
                'percent_correct': round(percent_correct, 1),
                'participation': f"{answered_count}/{total_questions}"
            }
        
        # Sort by total points (desc), then by percent correct (desc)
        leaderboard = sorted(
            student_scores.values(),
            key=lambda x: (x['total_points'], x['percent_correct']),
            reverse=True
        )
        
        # Add ranks
        for idx, entry in enumerate(leaderboard, start=1):
            entry['rank'] = idx
        
        return leaderboard
    
    def get_detailed_results(self, session: QuizSession) -> List[Dict]:
        """
        Get detailed results table for CSV export
        
        Args:
            session: QuizSession object
            
        Returns:
            List of result entries with per-question breakdown
        """
        from features.quiz import QuestionDataAccess
        question_data = QuestionDataAccess(self.db)
        
        leaderboard = self.calculate_leaderboard(session)
        questions = question_data.get_questions_by_quiz(session.quiz_id)
        all_answers = self.data_access.get_answers_by_session(session.id)
        
        # Map question IDs to question numbers
        question_map = {q.id: idx + 1 for idx, q in enumerate(questions)}
        
        detailed_results = []
        
        for entry in leaderboard:
            student_id = entry['student_id']
            
            # Get student's answers
            student_answers = [a for a in all_answers if a.student_id == student_id]
            
            # Build answer map (question_id -> option_order)
            answer_map = {}
            for answer in student_answers:
                if answer.selected_option:
                    # Convert option order to letter (1->A, 2->B, 3->C, 4->D)
                    option_letter = chr(64 + answer.selected_option.option_order)
                    answer_map[answer.question_id] = option_letter
            
            # Build result entry
            result = {
                'rank': entry['rank'],
                'student_name': entry['student_name'],
                'total_points': entry['total_points'],
                'percent_correct': entry['percent_correct'],
                'participation': entry['participation']
            }
            
            # Add per-question answers
            for question in questions:
                q_num = question_map[question.id]
                result[f'q{q_num}'] = answer_map.get(question.id, '-')
            
            detailed_results.append(result)
        
        return detailed_results
    
    # ==================== Additional Query Methods ====================
    
    def get_answers_by_session(self, session_id: Any):
        """
        Get all answers for a session
        
        Args:
            session_id: Session ID
        
        Returns:
            List of StudentAnswer instances
        """
        return self.data_access.get_answers_by_session(session_id)

