"""
Session code generation utilities
"""
import random
import string
from sqlalchemy.orm import Session
from config import SESSION_CODE_LENGTH


def generate_session_code(db: Session, length: int = SESSION_CODE_LENGTH) -> str:
    """
    Generate a unique session code
    
    Args:
        db: Database session
        length: Length of the code (default from config)
        
    Returns:
        Unique session code string
    """
    # Import here to avoid circular dependency
    from features.session import SessionDataAccess
    
    max_attempts = 100
    attempts = 0
    session_data = SessionDataAccess(db)
    
    while attempts < max_attempts:
        # Generate random numeric code
        code = ''.join(random.choices(string.digits, k=length))
        
        # Check if code already exists
        if not session_data.session_code_exists(code):
            return code
        
        attempts += 1
    
    # If we couldn't generate a unique code, raise an exception
    raise ValueError(f"Could not generate unique session code after {max_attempts} attempts")




