"""
Configuration module for Quiz Competition App
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'quizdb')
DB_USER = os.getenv('DB_USER', 'quizuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'quizpass')

# SQLAlchemy Database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# App Configuration
BASE_POINTS = 1000
SPEED_PENALTY_MULTIPLIER = 0.3
DEFAULT_QUESTION_TIME = 30  # seconds
SESSION_CODE_LENGTH = 5

# UI/UX Configuration
AUTO_REFRESH_ACTIVE_SESSION = 3  # seconds - for live session monitoring
AUTO_REFRESH_DASHBOARD = 10  # seconds - for dashboard updates
AUTO_REFRESH_LEADERBOARD = 5  # seconds - for leaderboard updates
AUTO_REFRESH_RESULTS = 10  # seconds - for results page
NOTIFICATION_DURATION = 3  # seconds
ACTIVITY_FEED_MAX_ITEMS = 20  # maximum activities to keep
STUDENTS_PER_PAGE = 50  # pagination for student list




