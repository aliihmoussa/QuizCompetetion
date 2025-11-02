"""
Student Dashboard - Join sessions and participate in quizzes
Following Streamlit best practices
"""
from orchestrators import StudentOrchestrator


def show_student_dashboard():
    """Main student dashboard"""
    orchestrator = StudentOrchestrator()
    orchestrator.show_dashboard()


