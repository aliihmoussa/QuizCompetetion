# 🎯 Quiz Competition App - Architecture Overview

> **Feature-Based Layered Architecture with Orchestrators**

---

## 📋 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [Architecture Layers](#️-architecture-layers)
3. [File Structure](#-file-structure)
4. [Data Flow](#-data-flow)
5. [Design Patterns](#-design-patterns)
6. [Key Components](#-key-components)
7. [Getting Started](#-getting-started)

---

## 🏗️ Architecture Overview

The Quiz Competition App follows a **feature-based, layered architecture** that separates concerns and promotes maintainability, testability, and scalability.

### Core Principles

- **Feature-based organization** - Each feature domain (quiz, session, scoring, student) is self-contained
- **Layered separation** - Clear boundaries between UI, business logic, and data access
- **Single responsibility** - Each class/module has one clear purpose
- **Dependency injection** - Services and data access layers receive database sessions via constructor
- **Base classes** - Common functionality extracted to base classes

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────┐
│   PRESENTATION LAYER                    │
│   (Pages → Orchestrators → UI Views)   │  ← Handles UI and user interaction
│   - pages/auth.py                       │
│   - orchestrators/*_orchestrator.py    │
│   - ui/instructor/*.py                  │
│   - ui/student/*.py                     │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   BUSINESS LOGIC LAYER                  │
│   (Services)                            │  ← Contains all business rules
│   - features/quiz/quiz_service.py      │
│   - features/session/session_service.py │
│   - features/scoring/scoring_service.py │
│   - features/student/student_service.py│
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   DATA ACCESS LAYER                     │
│   (Data Access Classes)                 │  ← Handles database operations
│   - features/*/*_data_access.py        │
│   - database/base_data_access.py       │
└─────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Components | What It Does | What It Doesn't Do |
|-------|-----------|--------------|-------------------|
| **Pages** | `pages/*.py` | Entry points, instantiate orchestrators | ❌ Business logic, ❌ Database queries |
| **Orchestrators** | `orchestrators/*.py` | Coordinate UI views, delegate to services | ❌ Direct database queries, ❌ Business logic |
| **UI Views** | `ui/instructor/*.py`, `ui/student/*.py` | Render UI components, handle user input | ❌ Database queries, ❌ Business logic |
| **Services** | `features/*/*_service.py` | Business rules, validation, orchestration | ❌ UI code, ❌ Direct SQL |
| **Data Access** | `features/*/*_data_access.py` | Database CRUD operations | ❌ UI code, ❌ Business logic |

---

## 📁 File Structure

```
quiz-competition-app/
│
├── 📱 app.py                    # Main Streamlit entry point
│                                # - Page configuration
│                                # - Session state management
│                                # - Route to appropriate page
│
├── 📄 pages/                    # ENTRY POINTS (Thin Layer)
│   ├── auth.py                  # → AuthOrchestrator
│   ├── instructor_dashboard.py  # → InstructorOrchestrator
│   └── student_dashboard.py     # → StudentOrchestrator
│
├── 🎮 orchestrators/            # PRESENTATION COORDINATION
│   ├── base_orchestrator.py     # Base orchestrator with common methods
│   ├── auth_orchestrator.py     # Authentication flow coordination
│   ├── instructor_orchestrator.py # Instructor features coordination
│   └── student_orchestrator.py  # Student features coordination
│
├── 🖼️ ui/                        # UI VIEW COMPONENTS
│   ├── components/              # Reusable UI components
│   ├── instructor/              # Instructor UI views
│   │   ├── dashboard.py         # Dashboard view
│   │   ├── quiz_management.py   # Quiz CRUD views
│   │   ├── session_management.py # Session control views
│   │   ├── results.py           # Results and analytics views
│   │   └── student_management.py # Student list and tracking
│   └── student/                 # Student UI views
│       ├── dashboard.py         # Student dashboard
│       ├── session_view.py      # Session participation view
│       └── leaderboard_view.py  # Leaderboard view
│
├── 💼 features/                 # FEATURE-BASED BUSINESS LOGIC
│   ├── quiz/                    # Quiz feature domain
│   │   ├── quiz_service.py      # Quiz business logic
│   │   ├── quiz_data_access.py  # Quiz data access
│   │   └── question_data_access.py # Question data access
│   ├── session/                 # Session feature domain
│   │   ├── session_service.py   # Session business logic
│   │   ├── session_data_access.py # Session data access
│   │   └── participant_data_access.py # Participant data access
│   ├── scoring/                 # Scoring feature domain
│   │   ├── scoring_service.py   # Scoring business logic
│   │   └── scoring_data_access.py # Scoring data access
│   └── student/                 # Student feature domain
│       ├── student_service.py   # Student business logic
│       └── student_data_access.py # Student data access
│
├── 🗃️ database/                 # DATA LAYER FOUNDATION
│   ├── __init__.py              # Database initialization
│   ├── connection.py            # Database connection management
│   ├── base_data_access.py      # Base data access class
│   ├── enums.py                 # Database enums (UserRole, SessionStatus)
│   └── models/                  # SQLAlchemy ORM models
│       ├── user.py
│       ├── quiz.py
│       ├── question.py
│       ├── question_option.py
│       ├── quiz_session.py
│       ├── session_participiant.py
│       └── student_ansawer.py
│
├── 🛠️ shared/                   # SHARED UTILITIES
│   ├── auth_helpers.py          # Authentication utilities
│   ├── session_code.py          # Session code generation
│   ├── styles.py                # CSS styling
│   ├── notifications.py         # Notification system
│   ├── auto_refresh.py          # Auto-refresh functionality
│   ├── ui_components.py         # Reusable UI components
│   └── core/                    # Core utilities
│       ├── decorators.py        # Function decorators
│       ├── state_manager.py     # Session state management
│       └── validators.py        # Input validation
│
└── ⚙️ Configuration
    ├── config.py                # Application configuration
    ├── requirements.txt          # Python dependencies
    ├── Dockerfile               # Docker configuration
    ├── docker-compose.yml       # Docker Compose setup
    └── env.example              # Environment variables template
```

---

## 🔄 Data Flow

### Example: Creating a Quiz

```
1. User Action
   └─> pages/instructor_dashboard.py
       └─> show_instructor_dashboard()
           └─> InstructorOrchestrator().show_dashboard()

2. Orchestrator
   └─> orchestrators/instructor_orchestrator.py
       └─> show_dashboard()
           └─> QuizManagementView().show_create_quiz()

3. UI View
   └─> ui/instructor/quiz_management.py
       └─> show_create_quiz()
           └─> Collects user input
           └─> Calls: quiz_service.create_quiz(...)

4. Service (Business Logic)
   └─> features/quiz/quiz_service.py
       └─> create_quiz()
           └─> Validates input
           └─> Calls: quiz_data_access.create_quiz(...)

5. Data Access
   └─> features/quiz/quiz_data_access.py
       └─> create_quiz()
           └─> Creates Quiz model
           └─> Saves to database
           └─> Returns Quiz instance

6. Response flows back up the chain
   └─> UI displays success message
```

### Key Points

- **Unidirectional flow** - Data flows down, responses flow up
- **No layer skipping** - Each layer only talks to adjacent layers
- **Services own business logic** - Validation and rules in services
- **Data access owns persistence** - Database operations in data access layer

---

## 🎨 Design Patterns

### 1. Repository Pattern (via Data Access)
```python
class QuizDataAccess(BaseDataAccess[Quiz]):
    def get_quiz_by_id(self, quiz_id):
        # Abstracted data access
        return self.get_by_id(Quiz, quiz_id)
```

### 2. Service Layer Pattern
```python
class QuizService:
    def create_quiz(self, instructor_id, title):
        # Business logic here
        if not title or len(title.strip()) < 3:
            raise ValueError("Title must be at least 3 characters")
        return self.quiz_data.create_quiz(instructor_id, title)
```

### 3. Orchestrator Pattern
```python
class InstructorOrchestrator(BaseOrchestrator):
    def show_dashboard(self):
        # Coordinates multiple views
        self._init_services()
        view = QuizManagementView(self.quiz_service)
        view.show_create_quiz()
```

### 4. Dependency Injection
```python
# Services receive database session via constructor
def __init__(self, db_session: Session):
    self.db = db_session
    self.quiz_data = QuizDataAccess(db_session)
```

### 5. Base Class Pattern
```python
# Common functionality in base classes
class BaseDataAccess(Generic[T]):
    def get_by_id(self, model_class, id):
        # Shared implementation
```

---

## 🔑 Key Components

### BaseOrchestrator
- Manages database sessions
- Provides common UI helpers (success/error messages)
- Handles user authentication state
- Provides logout functionality

### BaseDataAccess
- Generic CRUD operations (`get_by_id`, `get_all`, `create`, `update`, `delete`)
- Transaction management (`commit`, `rollback`, `flush`)
- Query building helpers

### Feature Services
- **QuizService**: Quiz and question management
- **SessionService**: Session lifecycle and participant management
- **ScoringService**: Score calculation and leaderboard generation
- **StudentService**: Student data and participation tracking

### Feature Data Access
Each feature has dedicated data access classes:
- Focused on specific domain entities
- Extends `BaseDataAccess` for common operations
- Implements domain-specific queries

---

## 🚀 Getting Started

### For New Developers

1. **Start with the flow:**
   - Read `app.py` to understand entry point
   - Follow a feature from page → orchestrator → UI → service → data access

2. **Understand the layers:**
   - Pages are thin entry points
   - Orchestrators coordinate UI views
   - UI views handle user interaction
   - Services contain business logic
   - Data access handles persistence

3. **Explore a feature:**
   - Pick one feature (e.g., quiz)
   - Read service class to understand business rules
   - Read data access class to understand data operations
   - Read UI views to understand user interaction

### Adding a New Feature

1. **Create feature structure:**
   ```
   features/new_feature/
   ├── __init__.py
   ├── new_feature_service.py
   └── new_feature_data_access.py
   ```

2. **Implement data access:**
   ```python
   class NewFeatureDataAccess(BaseDataAccess[NewModel]):
       def get_custom_data(self, ...):
           # Implement specific queries
   ```

3. **Implement service:**
   ```python
   class NewFeatureService:
       def __init__(self, db_session: Session):
           self.db = db_session
           self.data = NewFeatureDataAccess(db_session)
       
       def do_business_logic(self, ...):
           # Implement business rules
   ```

4. **Add UI view:**
   ```python
   class NewFeatureView:
       def __init__(self, service: NewFeatureService):
           self.service = service
       
       def show_ui(self):
           # Implement UI
   ```

5. **Integrate in orchestrator:**
   ```python
   class InstructorOrchestrator:
       def show_new_feature(self):
           self._init_services()
           view = NewFeatureView(self.new_feature_service)
           view.show_ui()
   ```

---

## ✅ Architecture Benefits

### Maintainability
- ✅ Clear separation of concerns
- ✅ Feature-based organization (easy to find code)
- ✅ Single responsibility per class
- ✅ Consistent patterns across codebase

### Testability
- ✅ Services can be tested without UI
- ✅ Data access can be tested independently
- ✅ Business logic separated from presentation
- ✅ Dependency injection enables mocking

### Scalability
- ✅ Easy to add new features
- ✅ Can extract services to API layer
- ✅ Database operations centralized
- ✅ Clear extension points

### Reusability
- ✅ Services can be reused (API, CLI, jobs)
- ✅ Base classes provide common functionality
- ✅ Shared utilities reduce duplication
- ✅ UI components are modular

---

## 📊 Architecture Statistics

| Component | Count | Purpose |
|-----------|-------|---------|
| **Orchestrators** | 3 | Coordinate features per user role |
| **UI Views** | 8+ | Modular UI components |
| **Services** | 4 | Feature business logic |
| **Data Access Classes** | 7+ | Database operations per feature |
| **Base Classes** | 2 | Common functionality |
| **Models** | 7 | Database entities |
| **Shared Utilities** | 10+ | Reusable helpers |

---

## 🎯 Best Practices

### Do's ✅
- ✅ Keep orchestrators thin - delegate to UI views
- ✅ Put business logic in services, not UI or data access
- ✅ Use type hints for better IDE support
- ✅ Follow feature-based organization
- ✅ Extend base classes for common operations
- ✅ Validate inputs in services

### Don'ts ❌
- ❌ Don't skip layers (UI → Service → Data Access)
- ❌ Don't put business logic in UI or data access
- ❌ Don't mix concerns in one class
- ❌ Don't create services without corresponding data access
- ❌ Don't put UI code in services or data access

---

## 🔮 Future Architecture Enhancements

- [ ] Add API layer (FastAPI) reusing services
- [ ] Add event-driven architecture for real-time updates
- [ ] Implement caching layer for frequently accessed data
- [ ] Add background job processing for heavy operations
- [ ] Implement domain events for audit trail
- [ ] Add GraphQL API layer

---

## 🆘 Troubleshooting

### Common Issues

**Q: Where do I add validation?**
A: In the Service layer. Services own all business rules.

**Q: Can I query the database directly in UI?**
A: No. Always go through Service → Data Access.

**Q: How do I add a new feature?**
A: Create feature module, add service and data access, create UI view, integrate in orchestrator.

**Q: Where should shared utilities go?**
A: In `shared/` directory. Core utilities in `shared/core/`.

---

## 🎉 Conclusion

This architecture provides a **solid foundation** for building and maintaining a scalable quiz competition application. The feature-based organization and clear layer separation make it easy to understand, test, and extend.

**Happy coding!** 🚀

---

**Architecture Version:** 2.0  
**Last Updated:** 2026  
**Status:** ✅ Production Ready
