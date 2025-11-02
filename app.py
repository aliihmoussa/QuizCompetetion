"""
Main Streamlit application entry point for Quiz Competition App
"""
import streamlit as st
from database import init_db, SessionLocal
from database.enums import UserRole
from shared.styles import inject_custom_css, COLORS
from shared.notifications import display_notifications

# -----------------------------
# Streamlit page configuration
# -----------------------------
st.set_page_config(
    page_title="Quiz Competition",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)

# -----------------------------
# Inject custom CSS
# -----------------------------
inject_custom_css()

# -----------------------------
# Initialize database
# -----------------------------
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {e}")

# -----------------------------
# Initialize session state
# -----------------------------
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'overview'

# -----------------------------
# Logout function
# -----------------------------
def logout():
    """Logout user and clear session"""
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# -----------------------------
# Top Navigation Bar
# -----------------------------
def render_top_nav():
    """Render modern top navigation bar"""
    # Navigation container
    st.markdown(
        f"""
        <div class="top-nav">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['primary']}; display: flex; align-items: center;">
                    <span style="margin-right: 0.5rem;">🏆</span>
                    Quiz Competition
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="color: {COLORS['text_secondary']}; font-weight: 500;">
                        {st.session_state.username}
                    </span>
                    <span style="padding: 0.25rem 0.75rem; background: {COLORS['primary_light']}; color: {COLORS['primary']}; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">
                        {st.session_state.role.value.upper() if st.session_state.role else ''}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# Main Application Logic
# -----------------------------
def main():
    """Main Streamlit application logic"""
    # Display any queued notifications
    display_notifications()
    
    # Show authentication page if user not logged in
    if not st.session_state.authenticated:
        from pages.auth import show_auth_page
        show_auth_page()
        return
    
    # Render top navigation
    render_top_nav()
    
    # Render page based on user role
    if st.session_state.role == UserRole.INSTRUCTOR:
        from pages.instructor_dashboard import show_instructor_dashboard
        show_instructor_dashboard()
    
    elif st.session_state.role == UserRole.STUDENT:
        from pages.student_dashboard import show_student_dashboard
        show_student_dashboard()
    
    else:
        st.error("Invalid user role")
        logout()
    
    # Logout button in sidebar (hidden by default but accessible)
    with st.sidebar:
        st.divider()
        if st.button("🚪 Logout", key="main_logout_button", use_container_width=True):
            logout()

# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    main()
