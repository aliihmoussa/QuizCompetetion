"""
Instructor Dashboard - Quiz management and session control
Following Streamlit best practices
"""
from orchestrators import InstructorOrchestrator


def show_instructor_dashboard():
    """Main instructor dashboard"""
    orchestrator = InstructorOrchestrator()
    orchestrator.show_dashboard()


