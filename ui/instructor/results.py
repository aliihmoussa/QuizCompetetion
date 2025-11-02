"""
Results Module
Display quiz results, analytics, and leaderboards
"""
import streamlit as st
import pandas as pd
from database.models import SessionStatus
from shared import ui_components as ui
from shared.styles import COLORS


class ResultsView:
    """View for displaying quiz results and analytics"""
    
    def __init__(self, session_service, scoring_service):
        """
        Initialize results view
        
        Args:
            session_service: SessionService instance
            scoring_service: ScoringService instance
        """
        self.session_service = session_service
        self.scoring_service = scoring_service
    
    def render(self, instructor_id):
        """
        Render results dashboard
        
        Args:
            instructor_id: UUID of the logged-in instructor
        """
        st.title("📊 Results Dashboard")
        
        try:
            sessions = self.session_service.get_instructor_sessions(
                instructor_id,
                SessionStatus.CLOSED
            )
            
            if not sessions:
                ui.info_card(
                    "📭 No Completed Sessions",
                    "Complete a session to see results here!"
                )
                return
            
            # Session selector
            session_options = {
                f"{s.quiz.title} - Code: {s.session_code} ({s.end_time.strftime('%Y-%m-%d %H:%M')})": s.id 
                for s in sessions
            }
            
            selected_session_name = st.selectbox(
                "Select Session to Analyze",
                options=list(session_options.keys())
            )
            
            session_id = session_options[selected_session_name]
            session = self.session_service.get_session(session_id)
            
            if not session:
                st.error("Session not found")
                return
            
            st.divider()
            
            # Session summary
            self._render_session_summary(session)
            
            st.divider()
            
            # Leaderboard
            self._render_leaderboard(session)
            
            # Export button
            st.divider()
            self._render_export_button(session)
        
        except Exception as e:
            st.error(f"Error loading results: {e}")
    
    def _render_session_summary(self, session):
        """Render session summary with key metrics"""
        st.markdown("### 📋 Session Summary")
        
        participants = self.session_service.get_participants(session.id)
        all_answers = self.scoring_service.get_answers_by_session(session.id)
        
        # Calculate statistics
        total_participants = len(participants)
        total_answers = len(all_answers)
        
        if session.start_time and session.end_time:
            duration = session.end_time - session.start_time
            duration_minutes = int(duration.total_seconds() // 60)
        else:
            duration_minutes = 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ui.metric_card(
                label="Quiz",
                value=session.quiz.title,
                delta=None
            )
        
        with col2:
            ui.metric_card(
                label="Participants",
                value=str(total_participants),
                delta=None
            )
        
        with col3:
            ui.metric_card(
                label="Total Answers",
                value=str(total_answers),
                delta=None
            )
        
        with col4:
            ui.metric_card(
                label="Duration",
                value=f"{duration_minutes} min",
                delta=None
            )
        
        # Session info card
        st.markdown(
            f"""
            <div style="background: {COLORS['background']}; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
                <div style="display: flex; justify-content: space-around; text-align: center;">
                    <div>
                        <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">Session Code</div>
                        <div style="color: {COLORS['text_primary']}; font-size: 1.25rem; font-weight: 700; font-family: monospace;">
                            {session.session_code}
                        </div>
                    </div>
                    <div>
                        <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">Started</div>
                        <div style="color: {COLORS['text_primary']}; font-size: 1.25rem; font-weight: 600;">
                            {session.start_time.strftime('%I:%M %p') if session.start_time else 'N/A'}
                        </div>
                    </div>
                    <div>
                        <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">Ended</div>
                        <div style="color: {COLORS['text_primary']}; font-size: 1.25rem; font-weight: 600;">
                            {session.end_time.strftime('%I:%M %p') if session.end_time else 'N/A'}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _render_leaderboard(self, session):
        """Render final leaderboard"""
        st.subheader("🏆 Final Leaderboard")
        leaderboard = self.scoring_service.calculate_leaderboard(session)
        
        if not leaderboard:
            st.info("No results to display")
            return
        
        # Display leaderboard
        for entry in leaderboard[:10]:
            rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry['rank'], f"{entry['rank']}.")
            
            # Create styled leaderboard entry
            st.markdown(
                f"""
                <div style="
                    background: {'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)' if entry['rank'] == 1 else 
                                'linear-gradient(135deg, #C0C0C0 0%, #808080 100%)' if entry['rank'] == 2 else
                                'linear-gradient(135deg, #CD7F32 0%, #8B4513 100%)' if entry['rank'] == 3 else
                                'white'};
                    padding: 1rem 1.5rem;
                    margin: 0.5rem 0;
                    border-radius: 10px;
                    border: 2px solid {COLORS['border']};
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                        <span style="font-size: 1.5rem; font-weight: 700;">{rank_emoji}</span>
                        <span style="font-size: 1.1rem; font-weight: 600; color: {COLORS['text_primary']};">
                            {entry['student_name']}
                        </span>
                    </div>
                    <div style="display: flex; gap: 2rem; align-items: center;">
                        <div style="text-align: center;">
                            <div style="font-size: 0.75rem; color: {COLORS['text_secondary']};">Points</div>
                            <div style="font-size: 1.1rem; font-weight: 700; color: {COLORS['primary']};">
                                ⭐ {entry['total_points']}
                            </div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.75rem; color: {COLORS['text_secondary']};">Accuracy</div>
                            <div style="font-size: 1.1rem; font-weight: 700; color: {COLORS['success']};">
                                ✅ {entry['percent_correct']}%
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    def _render_export_button(self, session):
        """Render export results button"""
        if st.button("📥 Export Session Results as CSV", use_container_width=True):
            detailed_results = self.scoring_service.get_detailed_results(session)
            df = pd.DataFrame(detailed_results)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"quiz_results_{session.session_code}_{session.end_time.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
