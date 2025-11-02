"""
Authentication page - Login and Registration
Following Streamlit best practices
"""
from orchestrators import AuthOrchestrator


def show_auth_page():
    """Display authentication page with login and registration tabs"""
    orchestrator = AuthOrchestrator()
    orchestrator.show_auth_page()



