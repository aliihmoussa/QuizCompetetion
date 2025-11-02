"""
Base Orchestrator class with common UI functionality
Following Streamlit best practices for modular architecture
"""
import streamlit as st
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from database import SessionLocal


class BaseOrchestrator:
    """
    Base orchestrator class providing common orchestrator functionality
    Enforces Orchestrator → View → Service → Data Access architecture
    """
    
    def __init__(self):
        """Initialize controller with database session"""
        self.db: Optional[Session] = None
    
    def _get_db(self) -> Session:
        """
        Get database session (private method)
        
        Returns:
            SQLAlchemy session
        """
        if self.db is None:
            self.db = SessionLocal()
        return self.db
    
    def _get_user_uuid(self) -> Optional[UUID]:
        """
        Get current user's UUID from session state (private method)
        
        Returns:
            UUID object of current user, or None if not authenticated
        """
        user_id = st.session_state.get('user_id')
        if user_id:
            return UUID(user_id) if isinstance(user_id, str) else user_id
        return None
    
    def _show_success(self, message: str):
        """Show success message (private method)"""
        st.success(message)
    
    def _show_error(self, message: str):
        """Show error message (private method)"""
        st.error(message)
    
    def _show_info(self, message: str):
        """Show info message (private method)"""
        st.info(message)
    
    def _show_warning(self, message: str):
        """Show warning message (private method)"""
        st.warning(message)
    
    def _logout(self):
        """Logout user and clear session (private method)"""
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.authenticated = False
        if self.db:
            self.db.close()
            self.db = None
        st.rerun()

