# Quiz Competition App 🏆

A real-time quiz competition web application built with Python, Streamlit, and PostgreSQL. Inspired by ClassPoint's competition mode, this app allows instructors to create engaging quiz competitions where students compete based on correctness and speed.

## Features

### For Instructors
- 📝 Create and manage quizzes with multiple-choice questions
- 🎮 Start live quiz sessions with unique session codes
- 📊 Real-time participant tracking
- 🏆 Live leaderboard with scoring based on correctness and speed
- 📈 Detailed results and analytics
- 💾 Export results as CSV
- 🔐 Secure authentication and role-based access

### For Students
- 🎯 Join sessions with simple session codes
- ⚡ Real-time question participation
- 🏅 Live leaderboard updates
- 📊 View personal performance and rankings

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.11
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0
- **Containerization:** Docker & Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd quiz-competition-app
```

2. Create environment file:
```bash
cp env.example .env
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

4. Access the application:
```
Open your browser and navigate to: http://localhost:8501
```

### Without Docker (Local Development)

1. Install PostgreSQL 15

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=quizdb
export DB_USER=quizuser
export DB_PASSWORD=quizpass
```

5. Run the application:
```bash
streamlit run app.py
```

## Usage Guide

### Session Model

**Important:** One Quiz = One Session with ALL Questions

- When you start a session, ALL questions from that quiz are included
- Students join the session once and progress through all questions
- The session tracks progression and scores across all questions
- Leaderboard is calculated based on performance across all questions in the session

### For Instructors

1. **Register/Login** as an instructor
2. **Create a Quiz:**
   - Go to "Create Quiz"
   - Enter quiz title and description
   - Add questions with 4 options each (all questions will be part of one session)
   - Mark the correct answer
3. **Start a Session:**
   - Go to "My Quizzes"
   - Click "Start Session" on your quiz
   - ONE session is created for the ENTIRE quiz (all questions included)
   - Share the session code with students (displayed with QR code)
4. **Run the Competition:**
   - Navigate to "Active Session"
   - See participants join in real-time
   - Progress through questions
   - View leaderboard after each question
   - End session when complete
5. **Export Results:**
   - Click "Export Results as CSV" from the leaderboard

### For Students

1. **Register/Login** as a student
2. **Join a Session:**
   - Enter the session code provided by your instructor
   - Click "Join Session"
3. **Participate:**
   - Wait for questions to appear
   - Select your answer quickly (speed matters!)
   - View your ranking on the leaderboard
4. **View Results:**
   - See final rankings when the session ends

## Scoring System

- **Base Points:** 1000 points per correct answer
- **Speed Bonus:** Faster submissions get higher scores
  - Formula: `points = 1000 - (time_taken / time_limit) × 300`
- **Incorrect Answer:** 0 points
- **Leaderboard Ranking:** Sorted by total points, then by accuracy

## Database Schema

The application uses 7 main tables:
- `users` - User accounts (instructors and students)
- `quizzes` - Quiz definitions
- `questions` - Quiz questions
- `question_options` - Answer options for questions
- `quiz_sessions` - Active/past quiz sessions
- `session_participants` - Session participation tracking
- `student_answers` - Student responses with timestamps

## Project Structure

```
quiz-competition-app/
├── app.py                      # Main Streamlit entry point
├── config.py                   # Configuration and settings
├── database/
│   ├── __init__.py            # Database connection setup
│   ├── models.py              # SQLAlchemy ORM models
│   └── queries.py             # Database query functions
├── pages/
│   ├── auth.py                # Login/Registration page
│   ├── instructor_dashboard.py # Instructor interface
│   └── student_dashboard.py    # Student interface
├── utils/
│   ├── auth_helpers.py        # Authentication utilities
│   ├── session_code.py        # Session code generation
│   └── scoring.py             # Scoring and leaderboard logic
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Configuration

Environment variables (in `.env` or docker-compose.yml):

```env
DB_HOST=postgres          # Database host
DB_PORT=5432             # Database port
DB_NAME=quizdb           # Database name
DB_USER=quizuser         # Database user
DB_PASSWORD=quizpass     # Database password
```

Application settings (in `config.py`):

```python
BASE_POINTS = 1000                    # Points for correct answer
SPEED_PENALTY_MULTIPLIER = 0.3        # Speed penalty factor
DEFAULT_QUESTION_TIME = 30            # Default time limit (seconds)
SESSION_CODE_LENGTH = 5               # Length of session codes
```

## Development

### Running Tests

```bash
# TODO: Add tests
pytest
```

### Code Quality

The codebase follows:
- PEP 8 style guidelines
- Type hints where applicable
- Comprehensive docstrings

## Future Enhancements

- [ ] Advanced analytics dashboard
- [ ] Question bank management
- [ ] CSV import for questions
- [ ] Image support in questions
- [ ] True real-time updates with WebSockets
- [ ] Mobile-responsive design improvements
- [ ] Team competitions
- [ ] Customizable scoring formulas
- [ ] Question difficulty levels
- [ ] Student practice mode

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

---

Built with ❤️ using Python, Streamlit, and PostgreSQL


