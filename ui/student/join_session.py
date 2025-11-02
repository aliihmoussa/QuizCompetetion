"""
Join Session Module
Handles student session joining interface
"""
import streamlit as st
from shared.styles import COLORS


class JoinSessionView:
    """View for joining quiz sessions"""
    
    def __init__(self, session_service):
        """
        Initialize join session view
        
        Args:
            session_service: SessionService instance
        """
        self.session_service = session_service
    
    def render(self, student_id, on_join_success):
        """
        Render session join interface
        
        Args:
            student_id: UUID of the logged-in student
            on_join_success: Callback function when join is successful
        """
        # Modern gradient hero section
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
                border-radius: 20px;
                padding: 3rem 2rem;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(37, 99, 235, 0.2);
            ">
                <div style="
                    font-size: 4rem;
                    margin-bottom: 1rem;
                    animation: bounce 2s infinite;
                ">🎯</div>
                <h1 style="
                    color: white;
                    margin-bottom: 0.5rem;
                    font-size: 2.5rem;
                    font-weight: 700;
                    text-shadow: 0 2px 10px rgba(0,0,0,0.1);
                ">Ready to Challenge Yourself?</h1>
                <p style="
                    color: rgba(255, 255, 255, 0.9);
                    font-size: 1.1rem;
                    max-width: 600px;
                    margin: 0 auto;
                ">
                    Enter the session code from your instructor and join the quiz competition!
                </p>
            </div>
            
            <style>
                @keyframes bounce {{
                    0%, 100% {{ transform: translateY(0); }}
                    50% {{ transform: translateY(-10px); }}
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Modern card-style form
        col1, col2, col3 = st.columns([1, 2.5, 1])
        
        with col2:
            st.markdown(
                f"""
                <div style="
                    background: white;
                    border-radius: 16px;
                    padding: 2.5rem;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                    border: 1px solid {COLORS['border']};
                ">
                    <h3 style="
                        color: {COLORS['text_primary']};
                        margin: 0 0 0.5rem 0;
                        font-size: 1.3rem;
                        font-weight: 600;
                    ">Enter Session Code</h3>
                    <p style="
                        color: {COLORS['text_secondary']};
                        margin: 0 0 1.5rem 0;
                        font-size: 0.95rem;
                    ">Type the 5-character code provided by your instructor</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with st.form("join_session_form", clear_on_submit=False):
                session_code = st.text_input(
                    "Session Code",
                    max_chars=10,
                    placeholder="e.g., ABC12",
                    key="session_code_input",
                    label_visibility="collapsed"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                submit = st.form_submit_button(
                    "🚀 Join Session",
                    use_container_width=True,
                    type="primary"
                )
                
                if submit and session_code:
                    self._handle_join(session_code.strip().upper(), student_id, on_join_success)
                elif submit:
                    st.error("⚠️ Please enter a session code")
        
        # Modern step-by-step instructions
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h3 style="color: {COLORS['text_primary']}; font-size: 1.5rem; margin-bottom: 2rem;">
                    How It Works
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self._render_step_card(
                step=1,
                title="Get Your Code",
                description="Your instructor will share a unique session code",
                color=COLORS['primary']
            )
        
        with col2:
            self._render_step_card(
                step=2,
                title="Enter & Join",
                description="Type the code above and click the join button",
                color=COLORS['secondary']
            )
        
        with col3:
            self._render_step_card(
                step=3,
                title="Start Quiz",
                description="Answer questions and compete with your peers!",
                color=COLORS['success']
            )
    
    def _render_step_card(self, step, title, description, color):
        """Render a single instruction step card"""
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 2rem 1.5rem;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                border: 2px solid {COLORS['primary_light']};
                transition: transform 0.2s;
            " onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, {color} 0%, {COLORS['primary_dark']} 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 1rem auto;
                    color: white;
                    font-size: 1.5rem;
                    font-weight: 700;
                    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
                ">{step}</div>
                <h4 style="color: {COLORS['text_primary']}; font-weight: 600; margin-bottom: 0.5rem; font-size: 1.1rem;">
                    {title}
                </h4>
                <p style="color: {COLORS['text_secondary']}; font-size: 0.9rem; margin: 0; line-height: 1.5;">
                    {description}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _handle_join(self, session_code, student_id, on_join_success):
        """Handle session join attempt"""
        try:
            result = self.session_service.join_session(session_code, student_id)
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                # Call the success callback
                on_join_success(result['session'])
            else:
                st.error(f"❌ {result['message']}")
        
        except Exception as e:
            st.error(f"Error joining session: {e}")

