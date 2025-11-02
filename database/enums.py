import enum


class UserRole(enum.Enum):
    """User role enumeration"""
    INSTRUCTOR = "instructor"
    STUDENT = "student"


class SessionStatus(enum.Enum):
    """Quiz session status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"
