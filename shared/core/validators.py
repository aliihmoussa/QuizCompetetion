"""
Input validation utilities
Provides reusable validators for forms and data processing
"""
import re
from typing import Any, Optional, Callable, List, Dict
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validator:
    """
    Fluent validator class for chainable validations
    
    Example:
        validator = Validator(email)
        validator.required().email().min_length(5).validate()
    """
    
    def __init__(self, value: Any, field_name: str = "Field"):
        """
        Initialize validator
        
        Args:
            value: Value to validate
            field_name: Name of field (for error messages)
        """
        self.value = value
        self.field_name = field_name
        self.errors: List[str] = []
    
    def required(self, message: Optional[str] = None) -> 'Validator':
        """Validate that value is not empty"""
        if self.value is None or (isinstance(self.value, str) and not self.value.strip()):
            self.errors.append(message or f"{self.field_name} is required")
        return self
    
    def min_length(self, length: int, message: Optional[str] = None) -> 'Validator':
        """Validate minimum length"""
        if self.value and len(str(self.value)) < length:
            self.errors.append(
                message or f"{self.field_name} must be at least {length} characters"
            )
        return self
    
    def max_length(self, length: int, message: Optional[str] = None) -> 'Validator':
        """Validate maximum length"""
        if self.value and len(str(self.value)) > length:
            self.errors.append(
                message or f"{self.field_name} must be at most {length} characters"
            )
        return self
    
    def email(self, message: Optional[str] = None) -> 'Validator':
        """Validate email format"""
        if self.value and not validate_email(self.value):
            self.errors.append(message or f"{self.field_name} must be a valid email")
        return self
    
    def matches(self, pattern: str, message: Optional[str] = None) -> 'Validator':
        """Validate against regex pattern"""
        if self.value and not re.match(pattern, str(self.value)):
            self.errors.append(
                message or f"{self.field_name} format is invalid"
            )
        return self
    
    def numeric(self, message: Optional[str] = None) -> 'Validator':
        """Validate that value is numeric"""
        try:
            float(self.value)
        except (ValueError, TypeError):
            self.errors.append(message or f"{self.field_name} must be numeric")
        return self
    
    def min_value(self, min_val: float, message: Optional[str] = None) -> 'Validator':
        """Validate minimum numeric value"""
        try:
            if float(self.value) < min_val:
                self.errors.append(
                    message or f"{self.field_name} must be at least {min_val}"
                )
        except (ValueError, TypeError):
            pass  # Will be caught by numeric() if used
        return self
    
    def max_value(self, max_val: float, message: Optional[str] = None) -> 'Validator':
        """Validate maximum numeric value"""
        try:
            if float(self.value) > max_val:
                self.errors.append(
                    message or f"{self.field_name} must be at most {max_val}"
                )
        except (ValueError, TypeError):
            pass
        return self
    
    def one_of(self, allowed_values: List[Any], message: Optional[str] = None) -> 'Validator':
        """Validate that value is in allowed list"""
        if self.value not in allowed_values:
            self.errors.append(
                message or f"{self.field_name} must be one of: {', '.join(map(str, allowed_values))}"
            )
        return self
    
    def custom(self, validator_func: Callable[[Any], bool], message: str) -> 'Validator':
        """Custom validation function"""
        if not validator_func(self.value):
            self.errors.append(message)
        return self
    
    def is_valid(self) -> bool:
        """Check if validation passed"""
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Get list of validation errors"""
        return self.errors
    
    def validate(self) -> bool:
        """
        Validate and raise ValidationError if fails
        
        Returns:
            True if valid
        
        Raises:
            ValidationError if validation fails
        """
        if not self.is_valid():
            raise ValidationError(self.errors[0])
        return True


# Standalone validation functions
def validate_required(value: Any, field_name: str = "Field") -> bool:
    """
    Validate that value is not empty
    
    Args:
        value: Value to validate
        field_name: Name of field for error message
    
    Returns:
        True if valid
    
    Raises:
        ValidationError if invalid
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} is required")
    return True


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid email format, False otherwise
    """
    if not email:
        return False
    
    # Simple email regex (covers most cases)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_session_code(code: str) -> bool:
    """
    Validate session code format
    
    Args:
        code: Session code to validate
    
    Returns:
        True if valid format, False otherwise
    """
    if not code:
        return False
    
    # Session code: 5-10 alphanumeric characters
    pattern = r'^[A-Z0-9]{5,10}$'
    return bool(re.match(pattern, code.upper()))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
    
    Returns:
        Dict with 'valid' boolean and 'errors' list
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'strength': 'strong' if len(errors) == 0 else 'weak'
    }


def validate_username(username: str) -> bool:
    """
    Validate username format
    
    Args:
        username: Username to validate
    
    Returns:
        True if valid format, False otherwise
    """
    if not username:
        return False
    
    # Username: 3-20 alphanumeric characters, underscores allowed
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))


def validate_quiz_title(title: str) -> bool:
    """
    Validate quiz title
    
    Args:
        title: Quiz title to validate
    
    Returns:
        True if valid
    
    Raises:
        ValidationError if invalid
    """
    if not title or not title.strip():
        raise ValidationError("Quiz title is required")
    
    if len(title) < 3:
        raise ValidationError("Quiz title must be at least 3 characters")
    
    if len(title) > 200:
        raise ValidationError("Quiz title must be at most 200 characters")
    
    return True


def validate_question_text(text: str) -> bool:
    """
    Validate question text
    
    Args:
        text: Question text to validate
    
    Returns:
        True if valid
    
    Raises:
        ValidationError if invalid
    """
    if not text or not text.strip():
        raise ValidationError("Question text is required")
    
    if len(text) < 5:
        raise ValidationError("Question text must be at least 5 characters")
    
    if len(text) > 1000:
        raise ValidationError("Question text must be at most 1000 characters")
    
    return True


def validate_time_limit(seconds: int) -> bool:
    """
    Validate time limit for questions
    
    Args:
        seconds: Time limit in seconds
    
    Returns:
        True if valid
    
    Raises:
        ValidationError if invalid
    """
    if seconds < 10:
        raise ValidationError("Time limit must be at least 10 seconds")
    
    if seconds > 300:
        raise ValidationError("Time limit must be at most 300 seconds (5 minutes)")
    
    return True


def validate_option_count(count: int) -> bool:
    """
    Validate number of options for a question
    
    Args:
        count: Number of options
    
    Returns:
        True if valid
    
    Raises:
        ValidationError if invalid
    """
    if count < 2:
        raise ValidationError("Question must have at least 2 options")
    
    if count > 6:
        raise ValidationError("Question can have at most 6 options")
    
    return True


def sanitize_input(text: str) -> str:
    """
    Sanitize user input (remove potentially harmful characters)
    
    Args:
        text: Text to sanitize
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove potential SQL injection patterns (basic)
    dangerous_patterns = [
        r';\s*DROP',
        r';\s*DELETE',
        r';\s*UPDATE',
        r';\s*INSERT',
        r'--',
        r'/\*',
        r'\*/'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()


class FormValidator:
    """
    Validate entire forms with multiple fields
    
    Example:
        form = FormValidator()
        form.add_field('email', email_value).email().required()
        form.add_field('password', password_value).min_length(8)
        
        if form.is_valid():
            # Process form
        else:
            show_errors(form.get_errors())
    """
    
    def __init__(self):
        """Initialize form validator"""
        self.fields: Dict[str, Validator] = {}
    
    def add_field(self, name: str, value: Any, field_label: Optional[str] = None) -> Validator:
        """
        Add field to validate
        
        Args:
            name: Field name
            value: Field value
            field_label: Display label for error messages
        
        Returns:
            Validator instance for chaining
        """
        validator = Validator(value, field_label or name)
        self.fields[name] = validator
        return validator
    
    def is_valid(self) -> bool:
        """Check if all fields are valid"""
        return all(v.is_valid() for v in self.fields.values())
    
    def get_errors(self) -> Dict[str, List[str]]:
        """Get all validation errors by field"""
        return {
            name: validator.get_errors()
            for name, validator in self.fields.items()
            if not validator.is_valid()
        }
    
    def get_all_errors(self) -> List[str]:
        """Get flat list of all errors"""
        all_errors = []
        for validator in self.fields.values():
            all_errors.extend(validator.get_errors())
        return all_errors
    
    def validate(self) -> bool:
        """
        Validate form and raise ValidationError if fails
        
        Returns:
            True if valid
        
        Raises:
            ValidationError with first error found
        """
        if not self.is_valid():
            errors = self.get_all_errors()
            raise ValidationError(errors[0])
        return True

