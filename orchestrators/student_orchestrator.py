"""
Student Orchestrator - Thin orchestrator layer
Delegates to focused view modules for each feature area
Following Streamlit best practices for modular architecture
"""
import streamlit as st
from features.session import SessionService
from features.quiz import QuizService
from features.scoring import ScoringService
from .base_orchestrator import BaseOrchestrator

# Note: Student views are modular and highly interactive


class StudentOrchestrator(BaseOrchestrator):
    """
    Orchestrator for student features
    Delegates to modular views for high interactivity
    Follows Orchestrator → View → Service → Data Access architecture
    """
    
    def __init__(self):
        """Initialize controller with lazy service loading"""
        super().__init__()
        # Services - initialized when needed
        self.session_service = None
        self.quiz_service = None
        self.scoring_service = None
    
    def _init_services(self):
        """Initialize all services with database session (lazy loading)"""
        if self.session_service is None:
            db = self._get_db()
            self.session_service = SessionService(db)
            self.quiz_service = QuizService(db)
            self.scoring_service = ScoringService(db)
    
    def show_dashboard(self):
        """Main student dashboard - routes to appropriate view"""
        # Sidebar
        with st.sidebar:
            st.title(f"👤 {st.session_state.username}")
            st.write("**Role:** Student")
            st.divider()
            
            # Show "Join Another Session" if already in a session
            if 'joined_session_id' in st.session_state:
                if st.button("🔄 Join Another Session", use_container_width=True):
                    if 'joined_session_id' in st.session_state:
                        del st.session_state.joined_session_id
                    if 'current_question_index' in st.session_state:
                        del st.session_state.current_question_index
                    st.rerun()
            
            st.divider()
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                self._handle_logout()
                st.rerun()
        
        # Main content - route based on state
        if 'joined_session_id' in st.session_state:
            # Import and use inline view for quiz participation
            from ui.student.quiz_participation import QuizParticipationView
            self._init_services()
            view = QuizParticipationView(
                self.session_service,
                self.quiz_service,
                self.scoring_service
            )
            view.render(st.session_state.joined_session_id, self._get_user_uuid())
        else:
            # Show join session form
            from ui.student.join_session import JoinSessionView
            self._init_services()
            view = JoinSessionView(self.session_service)
            view.render(self._get_user_uuid(), self._on_join_success)
    
    def _on_join_success(self, session):
        """Callback when session join is successful"""
        st.session_state.joined_session_id = session.id
        st.session_state.current_question_index = 0
        st.rerun()
    
    def _handle_logout(self):
        """Handle user logout"""
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

