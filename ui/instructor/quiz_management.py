"""
Quiz Management Module
Complete quiz and question management with inline editing
"""
import streamlit as st
from shared import ui_components as ui
from shared.styles import COLORS
from logging_config import get_logger

logger = get_logger("quiz_management")


class QuizManagementView:
    """View for managing quizzes and questions"""
    
    def __init__(self, quiz_service):
        """
        Initialize quiz management view
        
        Args:
            quiz_service: QuizService instance
        """
        self.quiz_service = quiz_service
    
    def render(self, instructor_id):
        """
        Render quiz management interface
        
        Args:
            instructor_id: UUID of the logged-in instructor
        """
        ui.section_header(
            "Quiz Management",
            "Create, edit, and organize your quizzes with questions",
            "📝"
        )
        
        try:
            logger.info(f"Rendering quiz management for instructor {instructor_id}")
            # Action buttons
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if st.button("➕ Create New Quiz", type="primary", use_container_width=True):
                    st.session_state.show_create_quiz_form = True
                    st.rerun()
            
            with col2:
                search_term = st.text_input("🔍 Search", placeholder="Search quizzes...", label_visibility="collapsed")
            
            with col3:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Recent", "Alphabetical", "Most Questions"],
                    label_visibility="collapsed"
                )
            
            st.divider()
            
            # Show create form if requested
            if st.session_state.get('show_create_quiz_form', False):
                self._render_create_quiz_form(instructor_id)
                st.divider()
            
            # Load and display quizzes
            quizzes = self.quiz_service.get_instructor_quizzes(instructor_id)
            
            if not quizzes:
                ui.info_card(
                    "No Quizzes Yet",
                    "Create your first quiz to get started!",
                    "📝"
                )
                return
            
            # Filter quizzes if search term provided
            if search_term:
                quizzes = [q for q in quizzes if search_term.lower() in q.title.lower() or 
                          (q.description and search_term.lower() in q.description.lower())]
            
            # Sort quizzes
            if sort_by == "Alphabetical":
                quizzes.sort(key=lambda x: x.title.lower())
            elif sort_by == "Most Questions":
                quiz_question_counts = {q.id: len(self.quiz_service.get_quiz_questions(q.id)) for q in quizzes}
                quizzes.sort(key=lambda x: quiz_question_counts.get(x.id, 0), reverse=True)
            
            st.markdown(f"### 📚 Your Quizzes ({len(quizzes)})")
            
            # Display quizzes
            for quiz in quizzes:
                self._render_quiz_card(quiz, instructor_id)
        
        except Exception as e:
            logger.error(f"Error loading quizzes for instructor {instructor_id}: {e}", exc_info=True)
            st.error(f"Error loading quizzes: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    def _render_create_quiz_form(self, instructor_id):
        """Render form to create a new quiz"""
        st.markdown("### ➕ Create New Quiz")
        
        with st.form("create_quiz_form", clear_on_submit=True):
            title = st.text_input("Quiz Title*", placeholder="e.g., Python Basics Quiz")
            description = st.text_area(
                "Description",
                placeholder="Brief description of what this quiz covers...",
                height=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Create Quiz", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel:
                st.session_state.show_create_quiz_form = False
                st.rerun()
            
            if submit:
                if not title:
                    st.error("Please provide a quiz title")
                else:
                    try:
                        quiz = self.quiz_service.create_quiz(
                            title=title.strip(),
                            description=description.strip() if description else None,
                            instructor_id=instructor_id
                        )
                        
                        if quiz:
                            st.success(f"✅ Quiz '{title}' created successfully!")
                            st.session_state.show_create_quiz_form = False
                            # Auto-expand to add questions
                            st.session_state[f'manage_questions_{quiz.id}'] = True
                            st.rerun()
                        else:
                            st.error("Failed to create quiz")
                    except Exception as e:
                        st.error(f"Failed to create quiz: {e}")
    
    def _render_quiz_card(self, quiz, instructor_id):
        """Render a single quiz card with inline management"""
        questions = self.quiz_service.get_quiz_questions(quiz.id)
        question_count = len(questions)
        
        # Check editing states
        is_editing = st.session_state.get(f'edit_quiz_{quiz.id}', False)
        is_managing_questions = st.session_state.get(f'manage_questions_{quiz.id}', False)
        
        if is_editing:
            self._render_edit_quiz_form(quiz, instructor_id)
        elif is_managing_questions:
            self._render_question_management(quiz, questions)
        else:
            # Display quiz card
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: white; padding: 1.5rem; margin: 1rem 0; border-radius: 12px; 
                                border: 2px solid {COLORS['border']}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <h3 style="color: {COLORS['primary']}; margin: 0 0 0.5rem 0; font-size: 1.25rem;">
                                    {quiz.title}
                                </h3>
                                <p style="color: {COLORS['text_secondary']}; margin: 0 0 0.75rem 0; font-size: 0.9rem;">
                                    {quiz.description if quiz.description else 'No description'}
                                </p>
                                <div style="color: {COLORS['text_secondary']}; font-size: 0.85rem;">
                                    📝 <strong>{question_count}</strong> question{'s' if question_count != 1 else ''}
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Action buttons
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button(f"✏️ Edit Quiz", key=f"edit_quiz_btn_{quiz.id}", use_container_width=True):
                        st.session_state[f'edit_quiz_{quiz.id}'] = True
                        st.rerun()
                
                with col2:
                    if st.button(f"🔧 Manage Questions ({question_count})", key=f"manage_q_{quiz.id}", use_container_width=True, type="primary"):
                        st.session_state[f'manage_questions_{quiz.id}'] = True
                        st.rerun()
                
                with col3:
                    if st.button(f"🎮 Start Session", key=f"start_{quiz.id}", use_container_width=True):
                        # Create session and navigate
                        try:
                            from features.session import SessionService
                            from database import get_db
                            
                            # Validate quiz has questions
                            questions = self.quiz_service.get_quiz_questions(quiz.id)
                            if not questions:
                                st.error(f"❌ Cannot start session: Quiz '{quiz.title}' has no questions. Please add questions first.")
                                st.stop()
                            
                            # Create session
                            st.info("Creating session...")
                            session_service = SessionService(get_db())
                            session = session_service.create_session(quiz.id, instructor_id)
                            
                            if session:
                                st.success(f"✅ Session created! Code: **{session.session_code}**")
                                st.balloons()
                                # Set session ID to view it in Active Session tab
                                st.session_state.active_session_id = session.id
                                st.info("💡 Navigate to 'Active Session' tab to start the session!")
                            else:
                                st.error("❌ Failed to create session - no session returned")
                        except Exception as e:
                            st.error(f"❌ Error creating session: {e}")
                            import traceback
                            st.code(traceback.format_exc(), language="python")
                            import logging
                            logging.error(f"Failed to create session for quiz {quiz.id}: {e}", exc_info=True)
                
                with col4:
                    if st.button(f"🗑️ Delete", key=f"del_quiz_{quiz.id}", type="secondary", use_container_width=True):
                        st.session_state[f'confirm_delete_quiz_{quiz.id}'] = True
                        st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f'confirm_delete_quiz_{quiz.id}', False):
                    st.warning(f"⚠️ Are you sure you want to delete '{quiz.title}'? This will delete all questions too!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Yes, Delete", key=f"confirm_del_{quiz.id}", type="primary"):
                            try:
                                success = self.quiz_service.delete_quiz(quiz.id)
                                if success:
                                    st.success("Quiz deleted successfully")
                                    del st.session_state[f'confirm_delete_quiz_{quiz.id}']
                                    st.rerun()
                                else:
                                    st.error("Failed to delete quiz")
                            except Exception as e:
                                st.error(f"Failed to delete: {e}")
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_del_{quiz.id}"):
                            del st.session_state[f'confirm_delete_quiz_{quiz.id}']
                            st.rerun()
    
    def _render_edit_quiz_form(self, quiz, instructor_id):
        """Render form to edit quiz metadata"""
        st.markdown(f"### ✏️ Editing Quiz: {quiz.title}")
        
        with st.form(f"edit_quiz_form_{quiz.id}"):
            new_title = st.text_input("Quiz Title*", value=quiz.title)
            new_description = st.text_area(
                "Description",
                value=quiz.description if quiz.description else "",
                height=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel:
                st.session_state[f'edit_quiz_{quiz.id}'] = False
                st.rerun()
            
            if submit:
                if not new_title:
                    st.error("Please provide a quiz title")
                else:
                    try:
                        result = self.quiz_service.update_quiz(
                            quiz_id=quiz.id,
                            title=new_title.strip(),
                            description=new_description.strip() if new_description else None
                        )
                        
                        if result:  # If quiz object returned, update succeeded
                            st.success("✅ Quiz updated successfully!")
                            st.session_state[f'edit_quiz_{quiz.id}'] = False
                            st.rerun()
                        else:
                            st.error("Failed to update quiz")
                    except Exception as e:
                        st.error(f"Failed to update quiz: {e}")
    
    def _render_question_management(self, quiz, questions):
        """Render inline question management interface"""
        st.markdown(f"### 🔧 Managing Questions: {quiz.title}")
        
        # Back button
        if st.button("⬅️ Back to Quizzes", key=f"back_from_manage_{quiz.id}"):
            st.session_state[f'manage_questions_{quiz.id}'] = False
            st.rerun()
        
        st.divider()
        
        # Add new question button
        if st.button("➕ Add New Question", key=f"add_new_q_{quiz.id}", type="primary", use_container_width=True):
            st.session_state[f'show_add_question_{quiz.id}'] = True
            st.rerun()
        
        # Show add question form
        if st.session_state.get(f'show_add_question_{quiz.id}', False):
            self._render_add_question_form(quiz, len(questions) + 1)
            st.divider()
        
        # Display existing questions
        if questions:
            st.markdown(f"#### 📝 Questions ({len(questions)})")
            for question in questions:
                self._render_question_card(quiz, question)
        else:
            st.info("No questions yet. Click 'Add New Question' to create one!")
    
    def _render_add_question_form(self, quiz, next_order):
        """Render form to add a new question"""
        st.markdown("### ➕ Add New Question")
        
        with st.form(f"add_question_form_{quiz.id}_{next_order}", clear_on_submit=True):
            question_text = st.text_area(
                "Question Text*",
                placeholder="Enter your question here...",
                height=100
            )
            
            time_limit = st.number_input(
                "Time Limit (seconds)",
                min_value=10,
                max_value=300,
                value=30,
                step=5
            )
            
            st.markdown("#### Options")
            st.caption("Mark the correct answer(s) with the checkbox")
            
            options = []
            for i in range(4):
                col1, col2 = st.columns([4, 1])
                with col1:
                    option_text = st.text_input(
                        f"Option {chr(65+i)}",
                        placeholder=f"Enter option {chr(65+i)}...",
                        key=f"opt_{i}_{quiz.id}_{next_order}"
                    )
                with col2:
                    is_correct = st.checkbox(
                        "Correct",
                        key=f"correct_{i}_{quiz.id}_{next_order}"
                    )
                
                if option_text:
                    options.append({
                        'text': option_text,
                        'order': i + 1,
                        'is_correct': is_correct
                    })
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("💾 Save Question", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel:
                st.session_state[f'show_add_question_{quiz.id}'] = False
                st.rerun()
            
            if submit:
                # Validation
                if not question_text:
                    st.error("Please enter a question")
                elif len(options) < 2:
                    st.error("Please provide at least 2 options")
                elif not any(opt['is_correct'] for opt in options):
                    st.error("Please mark at least one correct answer")
                else:
                    try:
                        question = self.quiz_service.add_question(
                            quiz_id=quiz.id,
                            question_text=question_text.strip(),
                            question_order=next_order,
                            options=options,
                            time_limit=time_limit
                        )
                        st.success("✅ Question added successfully!")
                        st.session_state[f'show_add_question_{quiz.id}'] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add question: {e}")
    
    def _render_question_card(self, quiz, question):
        """Render a single question card with edit capability"""
        is_editing = st.session_state.get(f'edit_question_{question.id}', False)
        
        if is_editing:
            self._render_edit_question_form(quiz, question)
        else:
            # Display question card
            with st.expander(f"Q{question.question_order}: {question.question_text[:60]}...", expanded=False):
                st.markdown(f"**Question:** {question.question_text}")
                st.markdown(f"**Time Limit:** {question.time_limit} seconds")
                
                if question.options:
                    st.markdown("**Options:**")
                    for opt in sorted(question.options, key=lambda x: x.option_order):
                        icon = "✅" if opt.is_correct else "○"
                        st.markdown(f"{icon} {chr(64 + opt.option_order)}. {opt.option_text}")
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_q_{question.id}", use_container_width=True):
                        st.session_state[f'edit_question_{question.id}'] = True
                        st.rerun()
                
                with col2:
                    if st.button(f"🗑️ Delete", key=f"del_q_{question.id}", type="secondary", use_container_width=True):
                        st.session_state[f'confirm_delete_q_{question.id}'] = True
                        st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f'confirm_delete_q_{question.id}', False):
                    st.warning("⚠️ Are you sure you want to delete this question?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Yes", key=f"confirm_del_q_{question.id}"):
                            try:
                                success = self.quiz_service.delete_question(question.id)
                                if success:
                                    st.success("Question deleted")
                                    del st.session_state[f'confirm_delete_q_{question.id}']
                                    st.rerun()
                                else:
                                    st.error("Failed to delete question")
                            except Exception as e:
                                st.error(f"Failed to delete question: {e}")
                    with col2:
                        if st.button("❌ No", key=f"cancel_del_q_{question.id}"):
                            del st.session_state[f'confirm_delete_q_{question.id}']
                            st.rerun()
    
    def _render_edit_question_form(self, quiz, question):
        """Render form to edit an existing question"""
        st.markdown(f"### ✏️ Editing Question {question.question_order}")
        
        with st.form(f"edit_question_form_{question.id}"):
            question_text = st.text_area(
                "Question Text*",
                value=question.question_text,
                height=100
            )
            
            time_limit = st.number_input(
                "Time Limit (seconds)",
                min_value=10,
                max_value=300,
                value=question.time_limit,
                step=5
            )
            
            st.markdown("#### Options")
            st.caption("Mark the correct answer(s) with the checkbox")
            
            # Pre-fill with existing options
            existing_options = sorted(question.options, key=lambda x: x.option_order)
            options = []
            
            for i in range(4):
                col1, col2 = st.columns([4, 1])
                
                # Get existing option if available
                existing_opt = existing_options[i] if i < len(existing_options) else None
                
                with col1:
                    option_text = st.text_input(
                        f"Option {chr(65+i)}",
                        value=existing_opt.option_text if existing_opt else "",
                        placeholder=f"Enter option {chr(65+i)}...",
                        key=f"edit_opt_{i}_{question.id}"
                    )
                with col2:
                    is_correct = st.checkbox(
                        "Correct",
                        value=existing_opt.is_correct if existing_opt else False,
                        key=f"edit_correct_{i}_{question.id}"
                    )
                
                if option_text:
                    options.append({
                        'text': option_text,
                        'order': i + 1,
                        'is_correct': is_correct
                    })
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("💾 Update Question", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel:
                st.session_state[f'edit_question_{question.id}'] = False
                st.rerun()
            
            if submit:
                # Validation
                if not question_text:
                    st.error("Please enter a question")
                elif len(options) < 2:
                    st.error("Please provide at least 2 options")
                elif not any(opt['is_correct'] for opt in options):
                    st.error("Please mark at least one correct answer")
                else:
                    try:
                        updated_question = self.quiz_service.update_question(
                            question_id=question.id,
                            question_text=question_text.strip(),
                            options=options,
                            time_limit=time_limit
                        )
                        if updated_question:
                            st.success("✅ Question updated successfully!")
                            st.session_state[f'edit_question_{question.id}'] = False
                            st.rerun()
                        else:
                            st.error("Failed to update question")
                    except Exception as e:
                        st.error(f"Failed to update question: {e}")
