# Quiz Competition App 🏆

A real-time quiz competition web application built with Python, Streamlit, and PostgreSQL. Inspired by ClassPoint's competition mode, this app allows instructors to create engaging quiz competitions where students compete based on correctness and speed.

## Features

### For Instructors
- 📝 Create and manage quizzes with multiple-choice questions
- ✏️ Edit existing quizzes and questions
- 🎮 Start live quiz sessions with unique session codes
- 📊 Real-time participant tracking
- 🏆 Live leaderboard with scoring based on correctness and speed
- 📈 Detailed results and analytics
- 💾 Export results as CSV
- 🔐 Secure authentication and role-based access
- 👥 Student management and tracking

### For Students
- 🎯 Join sessions with simple session codes
- ⚡ Real-time question participation
- 🏅 Live leaderboard updates
- 📊 View personal performance and rankings
- 📱 Modern, responsive UI

## Tech Stack

- **Frontend:** Streamlit 1.31.0
- **Backend:** Python 3.11+
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0
- **Containerization:** Docker & Docker Compose
- **Authentication:** bcrypt for password hashing
- **Utilities:** QR code generation, pandas, altair

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

Edit `.env` with your database credentials:
```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=quizdb
DB_USER=quizuser
DB_PASSWORD=quizpass
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

1. Install PostgreSQL 15 and create a database

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

Or create a `.env` file with the above variables.

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
   - Set time limit per question (default: 30 seconds)
3. **Edit Quizzes:**
   - Go to "My Quizzes"
   - Click "Edit" on any quiz
   - Modify quiz title, description, questions, or options
4. **Start a Session:**
   - Go to "My Quizzes"
   - Click "Start Session" on your quiz
   - ONE session is created for the ENTIRE quiz (all questions included)
   - Share the session code with students (displayed with QR code)
5. **Run the Competition:**
   - Navigate to "Active Session"
   - See participants join in real-time
   - Progress through questions
   - View leaderboard after each question
   - End session when complete
6. **View Results:**
   - Access detailed results from completed sessions
   - View leaderboards, individual student performance
   - Export results as CSV
7. **Student Management:**
   - View all registered students
   - See student participation history

### For Students

1. **Register/Login** as a student
2. **Join a Session:**
   - Enter the session code provided by your instructor
   - Click "Join Session"
3. **Participate:**
   - Wait for questions to appear
   - Select your answer quickly (speed matters!)
   - View your ranking on the leaderboard
   - Progress through all questions automatically
4. **View Results:**
   - See final rankings when the session ends
   - View your performance history

## Scoring System

- **Base Points:** 1000 points per correct answer
- **Speed Bonus:** Faster submissions get higher scores
  - Formula: `points = 1000 - (time_taken / time_limit) × 300`
- **Incorrect Answer:** 0 points
- **Leaderboard Ranking:** Sorted by total points, then by accuracy

## Database Schema

The application uses 7 main tables:
- `users` - User accounts (instructors and students) with UUID primary keys
- `quizzes` - Quiz definitions
- `questions` - Quiz questions with ordering
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
│   ├── connection.py          # Database connection management
│   ├── base_data_access.py    # Base data access layer
│   ├── enums.py               # Database enums (UserRole, SessionStatus)
│   └── models/                # SQLAlchemy ORM models
│       ├── user.py
│       ├── quiz.py
│       ├── question.py
│       ├── question_option.py
│       ├── quiz_session.py
│       ├── session_participiant.py
│       └── student_ansawer.py
├── pages/                      # Simple entry points
│   ├── auth.py                # Authentication page
│   ├── instructor_dashboard.py # Instructor dashboard entry
│   └── student_dashboard.py    # Student dashboard entry
├── orchestrators/              # Presentation layer orchestrators
│   ├── base_orchestrator.py   # Base orchestrator class
│   ├── auth_orchestrator.py   # Authentication orchestrator
│   ├── instructor_orchestrator.py # Instructor feature orchestrator
│   └── student_orchestrator.py    # Student feature orchestrator
├── ui/                         # UI view components
│   ├── components/            # Reusable UI components
│   ├── instructor/            # Instructor UI views
│   │   ├── dashboard.py
│   │   ├── quiz_management.py
│   │   ├── session_management.py
│   │   ├── results.py
│   │   └── student_management.py
│   └── student/               # Student UI views
│       ├── dashboard.py
│       ├── session_view.py
│       └── leaderboard_view.py
├── features/                   # Feature-based business logic
│   ├── quiz/                  # Quiz feature module
│   │   ├── quiz_service.py
│   │   ├── quiz_data_access.py
│   │   └── question_data_access.py
│   ├── session/                # Session feature module
│   │   ├── session_service.py
│   │   ├── session_data_access.py
│   │   └── participant_data_access.py
│   ├── scoring/                # Scoring feature module
│   │   ├── scoring_service.py
│   │   └── scoring_data_access.py
│   └── student/                # Student feature module
│       ├── student_service.py
│       └── student_data_access.py
├── shared/                     # Shared utilities
│   ├── auth_helpers.py        # Authentication utilities
│   ├── session_code.py        # Session code generation
│   ├── styles.py              # CSS styling
│   ├── notifications.py       # Notification system
│   ├── auto_refresh.py        # Auto-refresh functionality
│   ├── ui_components.py       # Reusable UI components
│   └── core/                  # Core utilities
│       ├── decorators.py
│       ├── state_manager.py
│       └── validators.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── env.example
└── README.md
```

## Architecture

The application follows a **feature-based, layered architecture**:

1. **Pages** - Entry points that instantiate orchestrators
2. **Orchestrators** - Coordinate UI views and delegate to services
3. **UI Views** - Modular UI components organized by user role
4. **Services** - Business logic organized by feature domain
5. **Data Access** - Database operations organized by feature domain
6. **Shared** - Common utilities and helpers

See [README_ARCHITECTURE.md](README_ARCHITECTURE.md) for detailed architecture documentation.

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
SPEED_PENALTY_MULTIPLIER = 0.3       # Speed penalty factor
DEFAULT_QUESTION_TIME = 30           # Default time limit (seconds)
SESSION_CODE_LENGTH = 5              # Length of session codes
AUTO_REFRESH_ACTIVE_SESSION = 3      # Auto-refresh interval (seconds)
```

## Development

### Code Organization

- **Feature-based modules** - Each feature (quiz, session, scoring, student) has its own service and data access layer
- **Separation of concerns** - UI, business logic, and data access are clearly separated
- **Base classes** - `BaseOrchestrator` and `BaseDataAccess` provide common functionality
- **Type hints** - Code includes type hints for better IDE support and documentation
- **UUID primary keys** - All entities use UUID for better distributed system support

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
- Feature-based organization

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
- [ ] Unit and integration tests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

---

Built with ❤️ using Python, Streamlit, and PostgreSQL
