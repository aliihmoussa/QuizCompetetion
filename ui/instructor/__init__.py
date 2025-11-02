"""
Instructor UI Modules
View components for instructor role
"""
from .dashboard import InstructorDashboardView
from .quiz_management import QuizManagementView
from .session_management import SessionManagementView
from .results import ResultsView
from .student_management import StudentManagementView

__all__ = [
    'InstructorDashboardView',
    'QuizManagementView',
    'SessionManagementView',
    'ResultsView',
    'StudentManagementView'
]
