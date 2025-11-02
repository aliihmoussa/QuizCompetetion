"""
Instructor Orchestrator - Thin orchestrator layer
Delegates to focused view modules for each feature area
Following Streamlit best practices for modular architecture
"""
import streamlit as st
from features.quiz import QuizService
from features.session import SessionService
from features.scoring import ScoringService
from features.student import StudentService
from .base_orchestrator import BaseOrchestrator

# Import view modules
from ui.instructor.dashboard import InstructorDashboardView
from ui.instructor.quiz_management import QuizManagementView
from ui.instructor.session_management import SessionManagementView
from ui.instructor.results import ResultsView
from ui.instructor.student_management import StudentManagementView


class InstructorOrchestrator(BaseOrchestrator):
    """
    Thin orchestrator for instructor features
    Delegates rendering to focused view modules
    Follows Orchestrator → View → Service → Data Access architecture
    """
    
    def __init__(self):
        """Initialize controller with lazy service loading"""
        super().__init__()
        # Services - initialized when needed
        self.quiz_service = None
        self.session_service = None
        self.scoring_service = None
        self.student_service = None
        
        # Views - initialized after services
        self.dashboard_view = None
        self.quiz_view = None
        self.session_view = None
        self.results_view = None
        self.student_view = None
    
    def _init_services(self):
        """Initialize all services with database session (lazy loading)"""
        if self.quiz_service is None:
            db = self._get_db()
            self.quiz_service = QuizService(db)
            self.session_service = SessionService(db)
            self.scoring_service = ScoringService(db)
            self.student_service = StudentService(db)
            
            # Initialize views with services
            self.dashboard_view = InstructorDashboardView(
                self.quiz_service,
                self.session_service,
                self.student_service,
                self.scoring_service
            )
            self.quiz_view = QuizManagementView(self.quiz_service)
            self.session_view = SessionManagementView(
                self.session_service,
                self.quiz_service,
                self.scoring_service,
                db
            )
            self.results_view = ResultsView(
                self.session_service,
                self.scoring_service
            )
            self.student_view = StudentManagementView(
                self.student_service,
                self.scoring_service
            )
    
    def show_dashboard(self):
        """Main dashboard entry point - routes to appropriate view"""
        self._init_services()
        instructor_id = self._get_user_uuid()
        
        # Navigation tabs
        tabs = st.tabs([
            "📊 Overview",
            "📝 My Quizzes",
            "🎮 Active Session",
            "📈 Results",
            "👥 Students"
        ])
        
        with tabs[0]:
            self.dashboard_view.render(instructor_id)
        
        with tabs[1]:
            self.quiz_view.render(instructor_id)
        
        with tabs[2]:
            self.session_view.render(instructor_id)
        
        with tabs[3]:
            self.results_view.render(instructor_id)
        
        with tabs[4]:
            self.student_view.render(instructor_id)

