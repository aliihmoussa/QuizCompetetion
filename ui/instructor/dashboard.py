"""
Instructor Dashboard Module
Overview dashboard with key metrics and active sessions
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from shared import ui_components as ui
from shared.auto_refresh import auto_refresh_component
from shared.styles import COLORS
import config


class InstructorDashboardView:
    """Dashboard overview for instructors"""
    
    def __init__(self, quiz_service, session_service, student_service, scoring_service):
        """
        Initialize dashboard view with required services
        
        Args:
            quiz_service: QuizService instance
            session_service: SessionService instance  
            student_service: StudentService instance
            scoring_service: ScoringService instance
        """
        self.quiz_service = quiz_service
        self.session_service = session_service
        self.student_service = student_service
        self.scoring_service = scoring_service
    
    def render(self, instructor_id):
        """
        Render the dashboard overview
        
        Args:
            instructor_id: UUID of the logged-in instructor
        """
        ui.section_header(
            "Dashboard Overview",
            "Welcome back! Here's what's happening with your quizzes.",
            "📊"
        )
        
        try:
            # Get statistics using services
            quiz_stats = self.quiz_service.get_quiz_stats(instructor_id)
            session_stats = self.session_service.get_session_stats(instructor_id)
            total_students = self.student_service.get_student_count(instructor_id)
            active_sessions_count = session_stats.get('active', 0)
            
            # Metrics Row
            st.markdown("### Key Metrics")
            self._render_metrics(quiz_stats, session_stats, total_students, active_sessions_count)
            
            st.divider()
            
            # Two column layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                self._render_recent_activity(instructor_id)
            
            with col2:
                self._render_active_sessions_panel(instructor_id, active_sessions_count)
            
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
    
    def _render_metrics(self, quiz_stats, session_stats, total_students, active_sessions_count):
        """Render key metrics cards"""
        cols = st.columns(4)
        
        with cols[0]:
            ui.metric_card(
                label="Total Quizzes",
                value=str(quiz_stats['total_quizzes']),
                delta=None
            )
        
        with cols[1]:
            ui.metric_card(
                label="Active Sessions",
                value=str(active_sessions_count),
                delta="Live now" if active_sessions_count > 0 else None,
                delta_positive=True
            )
        
        with cols[2]:
            ui.metric_card(
                label="Total Students",
                value=str(total_students),
                delta=None
            )
        
        with cols[3]:
            ui.metric_card(
                label="Completed Sessions",
                value=str(session_stats.get('closed', 0)),
                delta=None
            )
    
    def _render_recent_activity(self, instructor_id):
        """Render recent activity section"""
        st.markdown("### 📈 Recent Activity")
        
        # Get recent sessions
        recent_sessions = self.session_service.get_recent_sessions(instructor_id, limit=5)
        
        if recent_sessions:
            for session in recent_sessions:
                # Get participant count
                participants = self.session_service.get_participants(session.id)
                
                # Status badge
                if session.status.value == 'active':
                    status_badge = f"<span style='background: {COLORS['success_light']}; color: {COLORS['success']}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;'>● LIVE</span>"
                else:
                    status_badge = f"<span style='background: {COLORS['background']}; color: {COLORS['text_secondary']}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;'>ENDED</span>"
                
                # Format date
                if session.start_time:
                    time_str = session.start_time.strftime("%b %d, %I:%M %p")
                else:
                    time_str = "Not started"
                
                st.markdown(
                    f"""
                    <div style="background: white; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {COLORS['primary']}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <strong style="color: {COLORS['text_primary']}; font-size: 1rem;">{session.quiz.title}</strong>
                            {status_badge}
                        </div>
                        <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">
                            <span>🎯 Code: <strong>{session.session_code}</strong></span> &nbsp;&nbsp;
                            <span>👥 {len(participants)} participants</span> &nbsp;&nbsp;
                            <span>🕒 {time_str}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No recent sessions. Create a quiz and start a session!")
    
    def _render_active_sessions_panel(self, instructor_id, active_sessions_count):
        """Render active sessions panel"""
        st.markdown("### 🎮 Active Sessions")
        
        if active_sessions_count > 0:
            # Enable auto-refresh for active sessions
            auto_refresh_component(
                interval_seconds=config.AUTO_REFRESH_ACTIVE_SESSION,
                key="dashboard_active_sessions_refresh",
                label="Auto-refreshing active sessions"
            )
            
            active_sessions = self.session_service.get_active_sessions_with_details(instructor_id)
            
            for session_info in active_sessions:
                session = session_info['session']
                stats = session_info['stats']
                
                # Calculate completion
                total_possible = stats['participant_count'] * stats['question_count']
                completion = (stats['total_answers'] / total_possible * 100) if total_possible > 0 else 0
                
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%); padding: 1.25rem; margin: 0.75rem 0; border-radius: 10px; color: white; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);">
                        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem;">
                            {session.quiz.title}
                        </div>
                        <div style="background: rgba(255,255,255,0.15); padding: 0.5rem 0.75rem; border-radius: 6px; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.75rem; opacity: 0.9;">Session Code</span><br/>
                            <span style="font-size: 1.25rem; font-weight: 700; font-family: monospace;">{session.session_code}</span>
                        </div>
                        <div style="font-size: 0.85rem; opacity: 0.95;">
                            👥 {stats['participant_count']} students &nbsp;•&nbsp; 
                            📝 {stats['total_answers']}/{total_possible} answers &nbsp;•&nbsp; 
                            ✅ {completion:.0f}% complete
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Quick action button
                if st.button(
                    f"📊 Monitor {session.session_code}",
                    key=f"monitor_{session.id}",
                    use_container_width=True
                ):
                    st.session_state.active_session_id = session.id
                    st.session_state.instructor_page = "Active Session"
                    st.rerun()
        else:
            ui.info_card(
                "No Active Sessions",
                "Start a quiz session to see live updates here!"
            )
