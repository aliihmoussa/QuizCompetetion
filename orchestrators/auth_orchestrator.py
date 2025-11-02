"""
Authentication Orchestrator - Handles authentication UI
Following Streamlit best practices for auth flows
"""
import streamlit as st
from database.enums import UserRole
from features.student import StudentService
from .base_orchestrator import BaseOrchestrator


class AuthOrchestrator(BaseOrchestrator):
    """
    Orchestrator for authentication UI
    Follows Orchestrator → View → Service → Data Access architecture
    """
    
    def __init__(self):
        """Initialize controller with required services"""
        super().__init__()
        self.auth_service: StudentService = None
    
    def _init_services(self):
        """Initialize authentication service (private method)"""
        if self.auth_service is None:
            db = self._get_db()
            self.auth_service = StudentService(db)
    
    def show_auth_page(self):
        """Display authentication page with login and registration tabs"""
        st.title("🏆 Quiz Competition")
        st.markdown("### Welcome! Please login or register to continue.")
        
        # Initialize tab selection state
        if 'auth_tab' not in st.session_state:
            st.session_state.auth_tab = 0  # 0 = Login, 1 = Register
        
        # Create tabs for login and registration
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        # Login Tab
        with tab1:
            self.show_login_form()
        
        # Register Tab
        with tab2:
            self.show_register_form()
    
    def show_login_form(self):
        """Display login form"""
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    self._handle_login(username, password)
    
    def show_register_form(self):
        """Display registration form"""
        st.subheader("Register")
        
        with st.form("register_form"):
            username = st.text_input("Username", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            password_confirm = st.text_input("Confirm Password", type="password", key="register_password_confirm")
            role = st.selectbox("Role", options=[UserRole.STUDENT, UserRole.INSTRUCTOR], 
                               format_func=lambda x: x.value.capitalize())
            
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                self._handle_registration(username, email, password, password_confirm, role)
    
    def _handle_login(self, username: str, password: str):
        """Handle login logic (private method)"""
        self._init_services()
        
        try:
            user = self.auth_service.authenticate(username, password)
            
            if user:
                # Set session state (convert UUID to string for serialization)
                st.session_state.user_id = str(user.id)
                st.session_state.username = user.username
                st.session_state.role = user.role
                st.session_state.authenticated = True
                st.success(f"Welcome back, {user.username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        except Exception as e:
            st.error(f"Login error: {e}")
    
    def _handle_registration(
        self,
        username: str,
        email: str,
        password: str,
        password_confirm: str,
        role: UserRole
    ):
        """Handle registration logic (private method)"""
        # Validation
        if not username or not email or not password:
            st.error("Please fill in all fields")
            return
        
        if password != password_confirm:
            st.error("Passwords do not match")
            return
        
        self._init_services()
        
        try:
            result = self.auth_service.register(username, email, password, role)
            
            if result['success']:
                st.success("✅ Account created successfully! Redirecting to login...")
                # Clear form fields and redirect to login
                st.session_state.auth_tab = 0
                # Force a small delay to show success message
                import time
                time.sleep(1.5)
                st.rerun()
            else:
                st.error(result['message'])
        except Exception as e:
            st.error(f"Error creating account: {e}")

