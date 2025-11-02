"""
Session Management Module
Handles active session monitoring and control
"""
import streamlit as st
import qrcode
from io import BytesIO
from datetime import datetime
from database.models import SessionStatus
from shared import ui_components as ui
from shared.auto_refresh import auto_refresh_component
from shared.notifications import log_activity
from shared.styles import COLORS
import config


class SessionManagementView:
    """View for managing active sessions"""
    
    def __init__(self, session_service, quiz_service, scoring_service, db):
        """
        Initialize session management view
        
        Args:
            session_service: SessionService instance
            quiz_service: QuizService instance
            scoring_service: ScoringService instance
            db: Database session
        """
        self.session_service = session_service
        self.quiz_service = quiz_service
        self.scoring_service = scoring_service
        self.db = db
    
    def render(self, instructor_id):
        """
        Render active session monitoring interface
        
        Args:
            instructor_id: UUID of the logged-in instructor
        """
        try:
            # Get all active sessions for this instructor
            active_sessions = self.session_service.get_active_sessions_with_details(instructor_id)
            
            if not active_sessions:
                ui.empty_state(
                    "🎮",
                    "No Active Sessions",
                    "Start a quiz session from 'My Quizzes' tab to begin monitoring"
                )
                return
        
            # Enable auto-refresh for active sessions
            auto_refresh_component(
                interval_seconds=config.AUTO_REFRESH_ACTIVE_SESSION,
                key="active_session_refresh",
                label="Live session monitoring"
            )
            
            # If multiple active sessions, show selector
            if len(active_sessions) > 1:
                session = self._handle_multiple_sessions(active_sessions)
            else:
                # Only one active session
                session = active_sessions[0]['session']
                st.session_state.active_session_id = session.id
            
            # Check if session still active
            if not session or session.status == SessionStatus.CLOSED:
                st.warning("Session has ended.")
                if 'active_session_id' in st.session_state:
                    del st.session_state.active_session_id
                st.rerun()
                return
            
            # Display session monitoring interface
            self._render_session_monitor(session, instructor_id)
        
        except Exception as e:
            st.error(f"Error in active session: {e}")
    
    def _handle_multiple_sessions(self, active_sessions):
        """Handle session selection when multiple sessions are active"""
        st.markdown("### Select Active Session to Monitor")
        session_options = {
            f"{s['quiz_title']} - Code: {s['session'].session_code}": s['session'].id 
            for s in active_sessions
        }
        
        # Use the first session or the one from session_state
        default_session_id = st.session_state.get('active_session_id', active_sessions[0]['session'].id)
        
        # Find the default index
        default_index = 0
        for idx, (key, sid) in enumerate(session_options.items()):
            if sid == default_session_id:
                default_index = idx
                break
        
        selected_session_name = st.selectbox(
            "Choose session",
            options=list(session_options.keys()),
            index=default_index,
            key="session_selector"
        )
        
        selected_session_id = session_options[selected_session_name]
        st.session_state.active_session_id = selected_session_id
        return self.session_service.get_session(selected_session_id)
    
    def _render_session_monitor(self, session, instructor_id):
        """Render the main session monitoring interface"""
        # Title and refresh button
        col_title, col_refresh = st.columns([4, 1])
        
        with col_title:
            st.title(f"🎮 Active Session")
        
        with col_refresh:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_active_session"):
                # Force database refresh by clearing any cached queries
                self.db.expire_all()
                st.rerun()
        
        # Fetch fresh data
        self.db.expire_all()
        participants = self.session_service.get_participants(session.id)
        questions = self.quiz_service.get_quiz_questions(session.quiz_id)
        all_answers = self.scoring_service.get_answers_by_session(session.id)
        
        # Calculate completion statistics
        total_possible_answers = len(participants) * len(questions)
        total_submitted_answers = len(all_answers)
        completion_percentage = (total_submitted_answers / total_possible_answers * 100) if total_possible_answers > 0 else 0
        
        # Session summary card
        self._render_session_summary(session, participants, questions)
        
        # Metrics
        self._render_session_metrics(
            participants, 
            total_submitted_answers, 
            total_possible_answers, 
            completion_percentage, 
            session
        )
        
        # Show completion alert
        if completion_percentage == 100 and len(participants) > 0:
            st.success("🎉 **All students have completed all questions!** You can end the session now.")
        
        st.divider()
        
        # QR Code and Participants
        self._render_qr_and_participants(session, participants, all_answers, questions)
        
        st.divider()
        
        # Question controls
        self._render_question_controls(session, questions)
        
        st.divider()
        
        # End session button
        self._render_end_session_button(session, completion_percentage, participants)
    
    def _render_session_summary(self, session, participants, questions):
        """Render session summary card"""
        st.markdown(
            f"""
            <div class="custom-card" style="background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%); color: white; padding: 2rem; margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="color: white; margin: 0; font-size: 2rem;">{session.quiz.title}</h2>
                        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">
                            {len(participants)} participants • {len(questions)} questions
                        </p>
                    </div>
                    <div style="text-align: center; background: rgba(255,255,255,0.2); padding: 1.5rem 2rem; border-radius: 12px;">
                        <div style="font-size: 0.875rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">Session Code</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: white; font-family: monospace;">{session.session_code}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _render_session_metrics(self, participants, total_submitted, total_possible, completion, session):
        """Render session metrics cards"""
        cols = st.columns(4)
        
        with cols[0]:
            ui.metric_card(
                label="Participants",
                value=str(len(participants)),
                delta=None
            )
        
        with cols[1]:
            ui.metric_card(
                label="Total Answers",
                value=f"{total_submitted}/{total_possible}",
                delta=None
            )
        
        with cols[2]:
            ui.metric_card(
                label="Completion",
                value=f"{completion:.0f}%",
                delta="All done!" if completion == 100 else None,
                delta_positive=True
            )
        
        with cols[3]:
            # Calculate time elapsed
            if session.start_time:
                elapsed = datetime.utcnow() - session.start_time
                minutes = int(elapsed.total_seconds() // 60)
                ui.metric_card(
                    label="Time Elapsed",
                    value=f"{minutes} min",
                    delta=None
                )
            else:
                ui.metric_card(
                    label="Status",
                    value="Active",
                    delta="Live"
                )
    
    def _render_qr_and_participants(self, session, participants, all_answers, questions):
        """Render QR code and participants list"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            with st.expander("📱 QR Code", expanded=False):
                st.markdown(f"### Session Code: `{session.session_code}`")
                st.write("Students can scan this QR code to join")
                
                # Generate QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(session.session_code)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                buf = BytesIO()
                img.save(buf, format='PNG')
                st.image(buf.getvalue(), width=250)
        
        with col2:
            # Show timestamp of last update
            st.caption(f"🕒 Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            with st.expander(f"👥 Participants ({len(participants)})", expanded=True):
                if participants:
                    # Show participant completion status
                    for p in participants:
                        student_answers = [a for a in all_answers if a.student_id == p.student_id]
                        answered = len(student_answers)
                        total = len(questions)
                        percentage = (answered / total * 100) if total > 0 else 0
                        
                        if percentage == 100:
                            status_icon = "✅"
                            status_color = COLORS['success']
                        elif percentage > 0:
                            status_icon = "⏳"
                            status_color = COLORS['warning']
                        else:
                            status_icon = "⭕"
                            status_color = COLORS['text_muted']
                        
                        st.markdown(
                            f"""
                            <div style="padding: 0.5rem; margin: 0.25rem 0; background: {COLORS['background']}; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                                <span>{status_icon} <strong>{p.student.username}</strong></span>
                                <span style="color: {status_color}; font-weight: 600;">{answered}/{total}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No students have joined yet")
    
    def _render_question_controls(self, session, questions):
        """Render question navigation and control"""
        if not questions:
            return
        
        st.subheader("Quiz Questions")
        
        current_q_index = 0
        if session.current_question_id:
            for idx, q in enumerate(questions):
                if q.id == session.current_question_id:
                    current_q_index = idx
                    break
        
        # Display current question
        if current_q_index < len(questions):
            current_q = questions[current_q_index]
            
            st.markdown(f"### Question {current_q_index + 1}/{len(questions)}")
            st.write(f"**{current_q.question_text}**")
            
            for opt in current_q.options:
                st.write(f"{chr(64 + opt.option_order)}. {opt.option_text}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Show Answer", use_container_width=True):
                    for opt in current_q.options:
                        if opt.is_correct:
                            st.success(f"Correct Answer: {chr(64 + opt.option_order)}")
            
            with col2:
                if current_q_index < len(questions) - 1:
                    if st.button("Next Question", use_container_width=True):
                        result = self.session_service.next_question(session.id)
                        if result['success']:
                            st.rerun()
                else:
                    if st.button("Finish Quiz", use_container_width=True, type="primary"):
                        self.session_service.end_session(session.id)
                        st.success("✅ All questions completed! Session ended automatically.")
                        del st.session_state.active_session_id
                        st.rerun()
            
            with col3:
                if st.button("View Leaderboard", use_container_width=True):
                    st.session_state.show_leaderboard_modal = True
                    st.session_state.leaderboard_session = session
                    st.rerun()
    
    def _render_end_session_button(self, session, completion_percentage, participants):
        """Render end session button"""
        # Different button text based on completion
        if completion_percentage == 100 and len(participants) > 0:
            button_text = "✅ End Session (All Complete)"
            button_type = "primary"
        else:
            button_text = "🛑 End Session"
            button_type = "secondary"
        
        if st.button(button_text, type=button_type, use_container_width=True, key="end_session_btn"):
            # End the session
            self.session_service.end_session(session.id)
            
            # Log activity
            log_activity(
                "Session Ended",
                f"Ended session for {session.quiz.title}",
                "🛑",
                "session"
            )
            
            # Clear session state
            if 'active_session_id' in st.session_state:
                del st.session_state.active_session_id
            
            st.success("✅ Session ended successfully!")
            st.rerun()
