"""
Quiz Participation Module
Handles active quiz participation for students
"""
import streamlit as st
from database.models import SessionStatus
from shared.auto_refresh import auto_refresh_component
from shared.styles import COLORS
import config


class QuizParticipationView:
    """View for participating in active quiz sessions"""
    
    def __init__(self, session_service, quiz_service, scoring_service):
        """
        Initialize quiz participation view
        
        Args:
            session_service: SessionService instance
            quiz_service: QuizService instance
            scoring_service: ScoringService instance
        """
        self.session_service = session_service
        self.quiz_service = quiz_service
        self.scoring_service = scoring_service
    
    def render(self, session_id, student_id):
        """
        Render quiz participation interface
        
        Args:
            session_id: UUID of the joined session
            student_id: UUID of the logged-in student
        """
        try:
            session = self.session_service.get_session(session_id)
            
            if not session:
                st.error("Session not found")
                del st.session_state.joined_session_id
                return
            
            if session.status == SessionStatus.CLOSED:
                st.warning("This session has ended")
                self._show_final_results(session, student_id)
                
                if st.button("Leave Session", key="leave_session_closed"):
                    del st.session_state.joined_session_id
                    if 'current_question_index' in st.session_state:
                        del st.session_state.current_question_index
                    st.rerun()
                return
            
            # Enable auto-refresh
            auto_refresh_component(
                interval_seconds=config.AUTO_REFRESH_LEADERBOARD,
                key="student_quiz_refresh",
                label="Live updates enabled",
                show_indicator=True
            )
            
            # Render header
            self._render_session_header(session)
            
            # Get questions
            questions = self.quiz_service.get_quiz_questions(session.quiz_id)
            
            if not questions:
                st.error("No questions found in this quiz")
                return
            
            # Get student's answers
            student_answers = self.scoring_service.get_student_answers(session_id, student_id)
            answered_ids = {a.question_id for a in student_answers}
            answered_count = len(answered_ids)
            
            # Show progress
            self._render_progress(answered_count, len(questions))
            
            # Question navigation
            if 'current_question_index' not in st.session_state:
                st.session_state.current_question_index = 0
            
            current_index = st.session_state.current_question_index
            
            if current_index >= len(questions):
                # All questions completed
                st.success("🎉 **Congratulations! You've answered all questions!**")
                self._render_leaderboard(session, student_id)
                
                if st.button("Leave Session", key="leave_completed"):
                    del st.session_state.joined_session_id
                    del st.session_state.current_question_index
                    st.rerun()
                return
            
            current_question = questions[current_index]
            
            # Render question
            self._render_question(
                session,
                current_question,
                questions,
                current_index,
                student_id,
                answered_ids
            )
        
        except Exception as e:
            st.error(f"Error loading quiz: {e}")
    
    def _render_session_header(self, session):
        """Render modern session header"""
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
                border-radius: 16px;
                padding: 2rem 2rem;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 8px 25px rgba(37, 99, 235, 0.15);
            ">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🎮</div>
                <h2 style="color: white; margin-bottom: 0.5rem; font-size: 1.8rem; font-weight: 700;">
                    {session.quiz.title}
                </h2>
                <div style="
                    display: inline-block;
                    background: rgba(255, 255, 255, 0.2);
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                ">
                    <span style="color: white; font-size: 0.9rem; font-weight: 600;">
                        Session Code: <strong>{session.session_code}</strong>
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _render_progress(self, answered, total):
        """Render progress bar"""
        progress_percent = int((answered / total * 100)) if total > 0 else 0
        
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                border: 1px solid {COLORS['border']};
            ">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                    <span style="color: {COLORS['text_primary']}; font-weight: 600;">Your Progress</span>
                    <span style="color: {COLORS['primary']}; font-weight: 700; font-size: 1.1rem;">
                        {answered}/{total}
                    </span>
                </div>
                <div style="
                    background: {COLORS['background']};
                    border-radius: 10px;
                    height: 12px;
                    overflow: hidden;
                ">
                    <div style="
                        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
                        height: 100%;
                        width: {progress_percent}%;
                        transition: width 0.5s ease;
                        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
                    "></div>
                </div>
                <div style="text-align: center; color: {COLORS['text_secondary']}; font-size: 0.85rem; margin-top: 0.5rem;">
                    {progress_percent}% Complete
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _render_question(self, session, question, all_questions, current_index, student_id, answered_ids):
        """Render current question with options"""
        # Question counter
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="
                    display: inline-block;
                    background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
                    color: white;
                    padding: 0.5rem 1.5rem;
                    border-radius: 20px;
                    font-weight: 700;
                    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
                ">
                    Question {question.question_order} of {len(all_questions)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Check if already answered
        existing_answer = next((a for a in self.scoring_service.get_student_answers(session.id, student_id) 
                               if a.question_id == question.id), None)
        
        # Constrained width for question
        col_left, col_center, col_right = st.columns([0.5, 4, 0.5])
        
        with col_center:
            # Question card
            st.markdown(
                f"""
                <div style="
                    background: white;
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 0.5rem 0 1.5rem 0;
                    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
                    border-left: 4px solid {COLORS['primary']};
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <h3 style="color: {COLORS['text_primary']}; font-size: 1.15rem; margin: 0; font-weight: 600; flex: 1;">
                            {question.question_text}
                        </h3>
                        <span style="
                            background: {COLORS['accent_light']};
                            color: {COLORS['accent_dark']};
                            padding: 0.35rem 0.85rem;
                            border-radius: 16px;
                            font-size: 0.8rem;
                            font-weight: 600;
                            white-space: nowrap;
                        ">
                            ⏱️ {question.time_limit}s
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Options
            options = sorted(question.options, key=lambda x: x.option_order)
            
            if existing_answer:
                # Show answered options (read-only)
                st.success("✅ Answer Submitted", icon="✅")
                self._render_answered_options(options, existing_answer)
            else:
                # Show interactive options
                self._render_interactive_options(options, question, session, student_id, all_questions, current_index)
            
            # Navigation
            self._render_navigation(current_index, len(all_questions), answered_ids)
    
    def _render_answered_options(self, options, existing_answer):
        """Render options in read-only mode after answering"""
        for i in range(0, len(options), 2):
            col1, col2 = st.columns(2)
            
            option = options[i]
            is_selected = option.id == existing_answer.option_id
            
            with col1:
                self._render_option_display(option, is_selected)
            
            if i + 1 < len(options):
                option = options[i + 1]
                is_selected = option.id == existing_answer.option_id
                
                with col2:
                    self._render_option_display(option, is_selected)
    
    def _render_option_display(self, option, is_selected):
        """Render a single option in display mode"""
        option_letter = chr(64 + option.option_order)
        
        st.markdown(
            f"""
            <div style="
                background: {'linear-gradient(135deg, ' + COLORS['primary'] + ', ' + COLORS['primary_dark'] + ')' if is_selected else 'white'}; 
                padding: 0.85rem 1rem; 
                margin: 0.35rem 0; 
                border-radius: 8px;
                border: 2px solid {COLORS['primary'] if is_selected else COLORS['border']};
                color: {'white' if is_selected else COLORS['text_primary']};
                box-shadow: {'0 4px 12px rgba(37, 99, 235, 0.25)' if is_selected else '0 1px 4px rgba(0, 0, 0, 0.05)'};
            ">
                <span style="
                    display: inline-block;
                    width: 24px;
                    height: 24px;
                    background: {'rgba(255, 255, 255, 0.3)' if is_selected else COLORS['primary_light']};
                    color: {'white' if is_selected else COLORS['primary']};
                    border-radius: 50%;
                    text-align: center;
                    line-height: 24px;
                    font-weight: 700;
                    font-size: 0.85rem;
                    margin-right: 0.65rem;
                ">{option_letter}</span>
                <span style="font-size: 0.95rem; font-weight: {'600' if is_selected else '500'};">
                    {option.option_text} {'✓' if is_selected else ''}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _render_interactive_options(self, options, question, session, student_id, all_questions, current_index):
        """Render interactive option buttons"""
        st.markdown(
            """
            <style>
            .compact-option button {
                background: white !important;
                border: 2px solid #E5E7EB !important;
                color: #111827 !important;
                padding: 0.85rem 1rem !important;
                border-radius: 8px !important;
                font-size: 0.95rem !important;
                text-align: left !important;
                transition: all 0.2s ease !important;
            }
            .compact-option button:hover {
                background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%) !important;
                color: white !important;
                border-color: #2563EB !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        for i in range(0, len(options), 2):
            col1, col2 = st.columns(2)
            
            option = options[i]
            option_letter = chr(64 + option.option_order)
            
            with col1:
                st.markdown('<div class="compact-option">', unsafe_allow_html=True)
                if st.button(
                    f"**{option_letter}**  {option.option_text}",
                    key=f"option_{option.id}_{question.id}",
                    use_container_width=True
                ):
                    self._submit_answer(session.id, question.id, option.id, student_id, all_questions, current_index)
                st.markdown('</div>', unsafe_allow_html=True)
            
            if i + 1 < len(options):
                option = options[i + 1]
                option_letter = chr(64 + option.option_order)
                
                with col2:
                    st.markdown('<div class="compact-option">', unsafe_allow_html=True)
                    if st.button(
                        f"**{option_letter}**  {option.option_text}",
                        key=f"option_{option.id}_{question.id}",
                        use_container_width=True
                    ):
                        self._submit_answer(session.id, question.id, option.id, student_id, all_questions, current_index)
                    st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_navigation(self, current_index, total_questions, answered_ids):
        """Render navigation buttons"""
        col1, col2 = st.columns(2)
        
        with col1:
            if current_index > 0:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.current_question_index -= 1
                    st.rerun()
        
        with col2:
            if current_index < total_questions - 1:
                if st.button("Next ➡️", use_container_width=True):
                    st.session_state.current_question_index += 1
                    st.rerun()
    
    def _submit_answer(self, session_id, question_id, option_id, student_id, all_questions, current_index):
        """Submit answer and move to next question"""
        result = self.scoring_service.submit_answer(session_id, student_id, question_id, option_id)
        
        if result['success']:
            # Move to next question
            if current_index < len(all_questions) - 1:
                st.session_state.current_question_index += 1
            else:
                st.session_state.current_question_index = len(all_questions)
            st.rerun()
        else:
            st.error(f"Error submitting answer: {result.get('message')}")
    
    def _render_leaderboard(self, session, student_id):
        """Render leaderboard"""
        st.markdown("### 🏆 Leaderboard")
        
        leaderboard = self.scoring_service.calculate_leaderboard(session)
        
        if leaderboard:
            for entry in leaderboard[:10]:
                is_current_user = str(entry['student_id']) == str(student_id)
                rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry['rank'], f"{entry['rank']}.")
                
                st.markdown(
                    f"""
                    <div style="
                        background: {'linear-gradient(135deg, ' + COLORS['primary'] + ', ' + COLORS['primary_dark'] + ')' if is_current_user else 'white'};
                        color: {'white' if is_current_user else COLORS['text_primary']};
                        padding: 1rem 1.5rem;
                        margin: 0.5rem 0;
                        border-radius: 10px;
                        border: 2px solid {COLORS['primary'] if is_current_user else COLORS['border']};
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <div style="display: flex; gap: 1rem; align-items: center;">
                            <span style="font-size: 1.5rem;">{rank_emoji}</span>
                            <span style="font-weight: 600;">
                                {entry['student_name']} {'(You)' if is_current_user else ''}
                            </span>
                        </div>
                        <div style="display: flex; gap: 1.5rem;">
                            <span>⭐ {entry['total_points']} pts</span>
                            <span>✅ {entry['percent_correct']}%</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    def _show_final_results(self, session, student_id):
        """Show final results when session ends"""
        st.info("📊 View your final results below")
        self._render_leaderboard(session, student_id)

