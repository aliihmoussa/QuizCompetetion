"""
Logging Configuration
Centralized logging setup for the application
"""
import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Log to file
        logging.FileHandler(log_dir / "app.log"),
        # Log to console
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger("quiz_app")

def get_logger(name: str):
    """
    Get a logger instance for a specific module
    
    Args:
        name: Module name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"quiz_app.{name}")

