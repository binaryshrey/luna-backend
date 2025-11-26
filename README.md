# Luna Backend – Track 2 ![Supabase Database](https://img.shields.io/badge/Database-Supabase-3ECF8E?logo=supabase&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white) ![Render](https://img.shields.io/badge/Hosted%20on-Render-46E3B7?logo=render&logoColor=white) ![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white) ![Built with FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-009688?logo=fastapi&logoColor=white) ![Pytest](https://img.shields.io/badge/Pytest-Tests%20Passing-0A9EDC?logo=pytest&logoColor=white)

This repository contains my implementation for Luna take home assignment.

It provides:

- A **recommendation engine** that:
  - Suggests **venues** for a user based on geography, engagement and popularity.
  - Suggests **people** to go with that user based on the social graph and shared venue preference.
- An **agent flow** that creates a **booking** when a plan is confirmed.
- A clean, modular **FastAPI + Postgres (Supabase)** backend designed so that the current heuristic ML models can be upgraded to more advanced ML models without changing the public APIs.

![API Docs](https://raw.githubusercontent.com/binaryshrey/luna-backend/refs/heads/main/res/docs.png)

<br/>

## Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Architecture](#2-architecture)
3. [Local Setup](#3-local-setup)
4. [DB (Supabase) Setup](#4-db-supabase-setup)
5. [Seeding the DB](#5-seeding-the-database)
6. [Running the Server + Deployment](#6-running-the-server--deployment)
7. [API Overview](#7-api-overview)
8. [Recommendation Algorithms & ML Design](#8-recommendation-algorithms--ml-design)
9. [Agent / Booking Flow](#9-agent--booking-workflow)
10. [Test Suite](#10-test-suite)
11. [AI Coding Agents & Tools Used](#11-ai-coding-agents--tools-used)
12. [Third-Party Resources & Citations](#12-third-party-resources--citations)
13. [Architecture Choices & Design Decisions](#13-architecture-choices--design-decisions)
14. [Future Improvements](#14-future-improvements)

<br/>

## 1. High-Level Overview

This backend implements:

- A **data model** for:
  - Users, venues, user–venue interactions, social edges, plans, participants, bookings.
- **Endpoints** for:
  - Users & venues.
  - Logging interactions (views, likes, dwell times).
  - Venue and people recommendations.
  - Plan creation & confirmation, which triggers an “agent” to create a booking.
- A **feature-based recommendation layer**:
  - Currently using interpretable heuristics.
  - Structured so that the same features can be fed to a learned model (e.g., logistic regression / ranking model / matrix factorization) later since we only have some dummy data as of now.

<br/>

## 2. Architecture

> 📊 **Detailed Diagrams**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for comprehensive architecture diagrams including data flows, entity relationships, and deployment architecture.

### 2.1 Tech Stack

- **Language:** Python 3.11+
- **Env / Packaging:** [`uv`](https://github.com/astral-sh/uv)
- **Web Framework:** FastAPI
- **Database:** PostgreSQL (via Supabase)
- **ORM:** SQLAlchemy 2.x
- **Config:** Pydantic settings + `.env`
- **HTTP Server:** Uvicorn

### 2.2 Project Layout

The intended structure:

```text
luna-backend/
  app/
    main.py                 # FastAPI app entrypoint

    core/
      config.py             # Pydantic settings (DATABASE_URL, ENV, etc.)

    db/
      session.py            # SQLAlchemy engine, SessionLocal, Base

    models/
      user.py               # User (id, handle, name, home_lat, home_lng, age)
      venue.py              # Venue (id, name, category, lat, lng, price_level, rating)
      interactions.py       # UserVenueInteraction (user_id, venue_id, type, dwell)
      social.py             # UserSocialEdge (user_id, other_user_id, relationship_type, strength)
      plan.py               # Plan, PlanParticipant
      booking.py            # Booking (created by agent)

    schemas/
      user.py               # Pydantic models for users
      venue.py              # Pydantic models for venues
      interactions.py
      social.py
      reco.py               # VenueReco, UserReco response DTOs
      plan.py               # PlanCreate, PlanRead, etc.
      booking.py

    api/
      deps.py               # DB session dependency
      users.py              # /users endpoints
      venues.py             # /venues and /venues/{id}/interactions
      reco.py               # /reco/venues, /reco/people
      plans.py              # /plans and /plans/{id}/confirm (agent trigger)
      bookings.py           # Booking read endpoints (if implemented)

    services/
      reco_service.py       # Core recommendation logic (features + scoring)
      agent_service.py      # Booking agent logic

    seed.py                 # Script to populate DB with sample data

  pyproject.toml            # Dependencies (managed by uv)
  README.md
```

The design is layered:

- `models/` define DB tables.
- `schemas/` define API input/output types.
- `api/` exposes HTTP routes.
- `services/` contain business logic (recommendation, agents).
- `seed.py` creates a rich, non-trivial dataset for testing and evaluation.

<br/>

## 3. Local Setup

> 🚀 **Quick Start**: If you want to get up and running fast, see [QUICKSTART.md](./QUICKSTART.md) for a condensed setup guide with troubleshooting tips.

### 3.1 Prerequisites

Before starting, ensure you have the following installed:

| Requirement    | Version            | Purpose                       | Installation                                                       |
| -------------- | ------------------ | ----------------------------- | ------------------------------------------------------------------ |
| **Python**     | 3.11+              | Runtime environment           | [python.org](https://www.python.org/downloads/)                    |
| **uv**         | Latest             | Fast Python package installer | `pip install uv` or see [uv docs](https://github.com/astral-sh/uv) |
| **PostgreSQL** | 14+                | Database (or use Supabase)    | [postgresql.org](https://www.postgresql.org/download/)             |
| **Git**        | Any recent version | Version control               | [git-scm.com](https://git-scm.com/downloads)                       |

**Optional but Recommended:**

- **Postman** or **httpie** for API testing
- **pgAdmin** or **DBeaver** for database management
- **Docker** (if you prefer containerized PostgreSQL)

### 3.2 Clone the Repository

```bash
git clone https://github.com/binaryshrey/luna-backend.git
cd luna-backend
```

### 3.3 Environment & Dependencies (with uv)

**uv** is a fast Python package installer and resolver written in Rust. It's significantly faster than pip and provides better dependency resolution.

#### Step 1: Create Virtual Environment

Create a local virtualenv in `.venv/`:

```bash
uv venv .venv
```

#### Step 2: Activate Virtual Environment

**On macOS/Linux:**

```bash
source .venv/bin/activate
```

**On Windows:**

```bash
.venv\Scripts\activate
```

#### Step 3: Install Dependencies

Install all dependencies from `pyproject.toml`:

```bash
uv sync --active
```

This command:

- Reads `pyproject.toml` and `uv.lock`
- Installs all required packages
- Ensures reproducible builds

#### Key Dependencies

The project uses the following major dependencies:

| Package               | Version  | Purpose                                       |
| --------------------- | -------- | --------------------------------------------- |
| **fastapi**           | 0.121.3+ | Modern web framework for building APIs        |
| **uvicorn[standard]** | 0.38.0+  | ASGI server for running FastAPI               |
| **sqlalchemy**        | 2.0.44+  | SQL toolkit and ORM                           |
| **psycopg2-binary**   | 2.9.11+  | PostgreSQL adapter                            |
| **pydantic**          | 2.12.4+  | Data validation using Python type annotations |
| **pydantic-settings** | 2.12.0+  | Settings management                           |
| **python-dotenv**     | 1.2.1+   | Environment variable management               |
| **numpy**             | 2.0+     | Numerical computing for ML features           |
| **scikit-learn**      | 1.7.2+   | Machine learning utilities                    |
| **pytest**            | 8.0.0+   | Testing framework                             |
| **pytest-asyncio**    | 0.23.0+  | Async support for pytest                      |
| **httpx**             | 0.27.0+  | HTTP client for testing                       |

To view all dependencies:

```bash
cat pyproject.toml
```

To update dependencies:

```bash
uv sync --upgrade
```

<br/>

## 4. DB (Supabase) Setup

This project uses Supabase Postgres, but works with any Postgres URL.

### 4.1 Get the Postgres Connection URL

In Supabase:

1. Go to your project.

2. Open Project Settings → Database.

3. Copy the connection URL

### 4.2 Configure .env

Create a .env file in project root:

```
touch .env
```

Add:

```
DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:5432/<database>
```

### Below is the snapshot of DB schema under Supabase

![DB Schema](https://raw.githubusercontent.com/binaryshrey/luna-backend/refs/heads/main/res/db_schema.png)

### Below is the snapshot of DB Tables under Supabase

![DB Tables](https://raw.githubusercontent.com/binaryshrey/luna-backend/refs/heads/main/res/db_tables.png)

### 4.3 SQLAlchemy Session

`app/db/session.py` defines:

- `engine` – SQLAlchemy engine bound to settings.database_url
- `SessionLocal` – DB session factory
- `Base` – declarative base for models

Tables are created via:

```
Base.metadata.create_all(bind=engine)
```

This is invoked in `seed.py` (and can also be called on startup if desired).

<br/>

## 5. Seeding the Database

To get meaningful recommendations, we pre-populate the DB with realistic data.

![DB Data](https://raw.githubusercontent.com/binaryshrey/luna-backend/refs/heads/main/res/db_data.png)

### 5.1 What seed.py Does

`app/seed.py`:

- Creates all tables if they don’t exist.
- Skips reseeding if users already exist (to avoid duplicate data).
- Inserts:

  - 20+ users centered around a city location (e.g., NYC):

    - Each has handle, name, age, home_lat, home_lng.

  - 20+ venues with:
    - name, description, category (bar, cafe, music, restaurant, comedy, karaoke, sports, etc.)
    - lat, lng, price_level, rating.

- User–venue interactions:

  - Interaction types: view, interest, like.
  - dwell_time_seconds for time spent looking at or engaging with a venue.

- Social graph:

  - UserSocialEdge rows connecting most users with different relationship types (friend, mutual, suggested) and strength in [0.3, 0.95].

- Plans & participants:
  - Sample plans created by various users at different venues.
  - Participants invited/accepted for those plans.

This gives a rich, non-trivial dataset to exercise the recommender and agent flows.

## 5.2 Running the Seed Script

```
uv run python -m app.seed
```

We’ll see a log like:

```
Seed data inserted: 24 users, 20 venues, XXX interactions, YYY social edges, 5 plans.
```

<br/>

## 6. Running the Server + Deployment

With .venv activated and .env configured:

```
uv run uvicorn app.main:app --reload
```

The server will be available at:

- API root: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

The service is deployed on render.com with the LIVE url as : [https://luna-backend-shkw.onrender.com/docs/](https://luna-backend-shkw.onrender.com/docs/)

![Deploy](https://raw.githubusercontent.com/binaryshrey/luna-backend/refs/heads/main/res/deploy.png)

<br/>

## 7. API Overview

### 7.1 Users

<b>List users</b>

```
GET /users/
```

<b>Get a specific user</b>

```
GET /users/{user_id}
```

<b>Create a user</b>

```
POST /users/
Content-Type: application/json

{
  "handle": "alice",
  "name": "Alice Chen",
  "age": 25,
  "home_lat": 40.73,
  "home_lng": -73.93
}
```

### 7.2 Venues

<b>List venues</b>

```
GET /venues/
```

<b>Get a specific venue</b>

```
GET /venues/{venue_id}
```

<b>Create a venue</b>

```
POST /venues/
Content-Type: application/json

{
  "name": "Sunset Rooftop Bar",
  "description": "Rooftop cocktails with skyline view.",
  "category": "bar",
  "lat": 40.7325,
  "lng": -73.99,
  "price_level": 3,
  "rating": 4.7
}
```

<b>Log a user–venue interaction</b>

```
POST /venues/{venue_id}/interactions
Content-Type: application/json

{
  "user_id": "UUID-of-user",
  "interaction_type": "like",          // "view" | "interest" | "like"
  "dwell_time_seconds": 240
}
```

These interactions are the behavioral signals used by the recommender.

### 7.3 Recommendations

#### 7.3.1 Venue Recommendations

```
GET /reco/venues/{user_id}?limit=10
```

<b>Example response:</b>

```
[
  {
    "venue_id": "a64a37b4-c246-43f7-8c69-890c4bce5688",
    "score": 0.87,
    "distance_km": 1.2
  },
  {
    "venue_id": "c24d38f6-ccc5-4a70-9ae6-a9f61250a88b",
    "score": 0.81,
    "distance_km": 0.9
  }
]
```

#### 7.3.2 People Recommendations

```
GET /reco/people/{user_id}?venue_id={optional_venue_id}&limit=10
```

<b>Example response:</b>

```
[
  {
    "user_id": "655de160-3617-4c45-8ab8-415391f53be1",
    "score": 0.82
  },
  {
    "user_id": "442d28a9-c2c0-41f1-be13-7bfdbd5bd97d",
    "score": 0.79
  }
]
```

If `venue_id` is provided, the ranking also considers how much each friend likes that specific venue and other venues in the same category.

### 7.4 Plans & Bookings (Agent Flow)

<b>Create a plan</b>

```
POST /plans/
Content-Type: application/json

{
  "organizer_id": "UUID-of-user",
  "venue_id": "UUID-of-venue",
  "start_time": "2025-11-25T19:00:00Z"
}
```

<b>Confirm a plan (triggers booking agent)</b>

```
POST /plans/{plan_id}/confirm
```

Upon confirmation, the backend:

- Validates the plan and participants.
- Calls the agent to create a Booking record for the plan.
- Sets the plan’s status (e.g., confirmed).

<b>Bookings</b>

Depending on implementation, something like:

```
GET /bookings/
GET /bookings/{plan_id}
```

and is used to fetch bookings created by the agent.

<br/>

## 8. Recommendation Algorithms & ML Design

All recommendation logic lives in `app/services/reco_service.py`.

The design is intentionally **feature-based**, so it is:

- **Interpretable** today using simple heuristics.
- **Easily replaceable** with an ML model later, because the features are already structured.

### 8.1 Formal Problem Setup

We treat the system as two related ranking problems.

#### **1. Venue Recommendation**

Given a user **u**, rank venues **v ∈ V** by a relevance score:

```
s(u, v)
```

#### **2. People Recommendation (Companion Recommendation)**

Given a user **u**, and optionally a venue **v**, rank potential companions **f ∈ F(u)** by:

```
c(u, f, v)
```

The current system computes these scores using:

- Hand-crafted features
- Weighted combinations

In a production ML system, the **same feature sets** can be used to train learned weights or nonlinear models.

### 8.2 Venue Recommendation – Features & Scoring

Implementation starts with:

```
def recommend_venues_for_user(
    db: Session,
    user_id: UUID,
    limit: int = 10,
) -> List[VenueReco]:
    ...
```

### 8.2.1 Feature Engineering

For every user–venue pair `(u, v)`, we compute the following features:

1. Spatial Distance d(u, v)

Inputs:

- User location: user.home_lat, user.home_lng
- Venue location: venue.lat, venue.lng

Compute using the Haversine formula:

```
dist_km = haversine_km(user.home_lat, user.home_lng, v.lat, v.lng)
```

Convert to a proximity score:

```
spatial_score = exp(-0.3 * dist_km)
```

Interpretation:

- Nearby venues → score close to 1
- Far venues → score decays quickly

2. User-Specific Preference Score

Retrieve all UserVenueInteraction rows for (u, v):

- Count like and interest interactions → like_count
- Sum dwell time → view_time (in seconds)

Compute:

```
preference_score = min(1.0, like_count * 0.5 + view_time / 300.0)
```

Meaning:

- Each like = +0.5
- Every 300 seconds of viewing = +1.0
- Capped at 1.0

3. Global Popularity Score

Count how many users liked or showed interest in each venue:

```
popularity_counts[v.id] = number_of_positive_interactions
```

Normalize:

```
popularity_score = popularity_counts[v.id] / max_popularity
```

The most popular venue gets 1.0, others fall between 0 and 1.

### 8.2.2 Final Venue Score

Combine all features:

```
venue_score = (
    0.4 * spatial_score +
    0.4 * preference_score +
    0.2 * popularity_score
)
```

Weights mean:

- 40% → distance/proximity
- 40% → personal preference
- 20% → global popularity

Sort venues by `venue_score` and return top-k recommendations.

### 8.3 People Recommendation – Features & Scoring

Entry point:

```
def recommend_people_for_user(
    db: Session,
    user_id: UUID,
    venue_id: UUID | None,
    limit: int = 10,
) -> List[UserReco]:
    ...
```

This function ranks friends/candidates for a user, optionally conditioned on a venue.

### 8.3.1 Base Social Graph (Core Feature)

From `UserSocialEdge`:

- `user_id` → main user
- `other_user_id` → friend candidate
- `relationship_type` → "friend", "mutual", "suggested"
- `strength` → numeric closeness in [0, 1]

Start with:

```
base_strength = float(edge.strength or 0.0)
```

This is the primary signal.

### 8.3.2 Venue-Conditioned Preference Signals

If `venue_id` is provided, we incorporate how aligned each friend is with that specific venue and its category.

Let v be the target venue.

1. Direct Preference for Venue v

Retrieve interactions where:

```
user_id = friend f
venue_id = target venue v
```

Compute:

```
direct_pref = min(
    1.0,
    direct_like_count * 0.5 + direct_view_time / 300.0
)
```

Represents how much this friend likes the same venue.

2. Category-Level Preference

Steps:

1. Identify the category of venue v.

2. Collect all venue IDs in that category.

3. Aggregate interactions for friend f across those venues.

Compute:

```
category_pref = min(
    1.0,
    cat_like_count * 0.3 + cat_view_time / 600.0
)
```

This is softer than direct venue preference.

### 8.3.3 Final People Score

Combine signals:

```
score = (
    0.6 * base_strength +
    0.25 * direct_pref +
    0.15 * category_pref
)
```

Meaning:

- 60% → social closeness
- 25% → preference for this venue
- 15% → preference for this category

If `venue_id` is omitted:

direct_pref = 0
category_pref = 0
score = 0.6 \* base_strength

<br/>

## 9. Agent / Booking Workflow

The “agent” logic lives in `app/services/agent_service.py` and is triggered via `app/api/plans.py`.

### 9.1 Conceptual Flow

1. User creates a plan:

```
POST /plans/
```

with:

```
{
  "organizer_id": "<user-uuid>",
  "venue_id": "<venue-uuid>",
  "start_time": "2025-11-25T19:00:00Z"
}
```

2. Friends are associated as PlanParticipant rows (seeded or via API).

3. Once the group agrees, client calls:

```
POST /plans/{plan_id}/confirm
```

4. The backend:

- Validates the plan & participants.
- Calls the agent service to:
  - Create a Booking linked to this plan_id.
  - Set some fields like provider ("mock"), status ("booked"), and a fake reference number.
- Updates the plan’s status to confirmed.

5. The booking can be fetched via booking endpoints for UI display.

### 9.2 Real-World Extension

In a real product:

- agent_service.py would:
  - Call external APIs (OpenTable, Ticketmaster, custom venue APIs).
  - Handle failures, retries, cancellations.
  - Potentially choose between multiple providers based on price, availability, or user preferences.

The current implementation focuses on the control flow and data model, so it’s easy to swap in real integrations.

<br/>

## 10. Test Suite

The test suite uses:

- **pytest** - Testing framework
- **httpx** - HTTP client for testing FastAPI endpoints
- **SQLite in-memory database** - For isolated, fast test execution

### Snapshot of test suite

![Tests](https://raw.githubusercontent.com/binaryshrey/luna-backend/refs/heads/main/res/tests.png)

### Running Tests

#### Run all tests

```
uv run pytest
```

#### Run with verbose output

```
uv run pytest -v
```

#### Run specific test file

```
uv run pytest tests/test_users.py
```

#### Run specific test

```
uv run pytest tests/test_users.py::test_create_user
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Test configuration and fixtures
├── test_health.py       # Health check endpoint tests
├── test_users.py        # User API endpoint tests
└── test_venues.py       # Venue API endpoint tests
```

### Test Coverage

#### Health API (`test_health.py`)

- Health check endpoint returns correct status
- Health check response structure validation

#### Users API (`test_users.py`)

- Create user with full data
- Create user with minimal required fields
- Duplicate handle validation
- List users (empty and populated)

#### Venues API (`test_venues.py`)

- Create venue with full data
- Create venue with minimal required fields
- List venues (empty and populated)

### Fixtures

#### `db_session`

Provides a fresh SQLite in-memory database session for each test. The database is automatically created and torn down for each test function.

#### `client`

Provides a FastAPI TestClient with the database dependency overridden to use the test database session.

#### Notes

- **Database**: Tests use SQLite in-memory database for speed and isolation
- **Test Isolation**: Each test runs with a fresh database to ensure test independence
- **Production vs Test**: The application uses PostgreSQL in production, but tests use SQLite for simplicity

### Adding New Tests

1. Create a new test file in the `tests/` directory (e.g., `test_plans.py`)
2. Import necessary fixtures and modules:
   ```python
   def test_my_feature(client):
       response = client.get("/my-endpoint/")
       assert response.status_code == 200
   ```
3. Use the `client` fixture to make requests to your API
4. Add assertions to verify expected behavior

### Continuous Integration

These tests are designed to run in CI/CD pipelines. They are fast, isolated, and don't require external dependencies.

<br/>

## 11. AI Coding Agents & Tools Used

This project leveraged several AI coding assistants and tools during development to enhance productivity and code quality:

### AI Assistants

#### **Claude (Anthropic)**

- **Usage**: Code review, refactoring suggestions, best practices
- **Specific Applications**:
  - Reviewed service layer architecture
  - Suggested improvements to separation of concerns
  - Provided feedback on API design patterns
  - Helped structure test fixtures and conftest.py
  - Advised on error handling patterns

### Development Tools

#### Code Quality & Formatting

- **Tools Used**: Python built-in linters, manual review
- **Note**: While the project doesn't currently use automated formatters like Black or Ruff, they are recommended for future iterations

#### Database Management

- **Supabase Web Interface**: Visual database management and query testing
- **SQLAlchemy**: ORM with automatic schema migration via `create_all()`

#### API Development & Testing

- **FastAPI Swagger UI**: Interactive API documentation at `/docs`
- **ReDoc**: Alternative API documentation at `/redoc`
- **Postman**: Manual endpoint testing (not in repository)

<br/>

## 12. Third-Party Resources & Citations

This project builds upon established technologies, libraries, and community resources. Below is a comprehensive attribution of external resources used:

### Core Frameworks & Libraries

#### **FastAPI** (Web Framework)

- **Source**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **License**: MIT
- **Usage**: Primary web framework for building REST API endpoints
- **Why Chosen**: Automatic OpenAPI documentation, type safety, async support, excellent performance

#### **SQLAlchemy** (ORM)

- **Source**: [https://www.sqlalchemy.org/](https://www.sqlalchemy.org/)
- **License**: MIT
- **Usage**: Database ORM for model definitions and queries
- **Documentation**: [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)

#### **Pydantic** (Data Validation)

- **Source**: [https://docs.pydantic.dev/](https://docs.pydantic.dev/)
- **License**: MIT
- **Usage**: Request/response validation, settings management
- **Version**: 2.x (uses new API)

#### **Uvicorn** (ASGI Server)

- **Source**: [https://www.uvicorn.org/](https://www.uvicorn.org/)
- **License**: BSD
- **Usage**: Production-ready ASGI server

### Database & Infrastructure

#### **Supabase** (Database Hosting)

- **Source**: [https://supabase.com/](https://supabase.com/)
- **Usage**: PostgreSQL database hosting with management UI
- **Why Chosen**: Free tier, excellent developer experience, built-in features

#### **PostgreSQL** (Database)

- **Source**: [https://www.postgresql.org/](https://www.postgresql.org/)
- **License**: PostgreSQL License (similar to MIT)
- **Version**: 14+

### Python Ecosystem Tools

#### **uv** (Package Manager)

- **Source**: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
- **License**: Apache 2.0 / MIT
- **Usage**: Fast Python package installer and resolver
- **Alternative to**: pip, poetry

#### **pytest** (Testing Framework)

- **Source**: [https://pytest.org/](https://pytest.org/)
- **License**: MIT
- **Usage**: Unit and integration testing

### Scientific Computing

#### **NumPy** (Numerical Computing)

- **Source**: [https://numpy.org/](https://numpy.org/)
- **License**: BSD
- **Usage**: Array operations for feature engineering

#### **scikit-learn** (Machine Learning)

- **Source**: [https://scikit-learn.org/](https://scikit-learn.org/)
- **License**: BSD
- **Usage**: ML utilities (currently for future expansion)

### Algorithms & Formulas

#### **Haversine Formula** (Distance Calculation)

- **Reference**: [Haversine formula - Wikipedia](https://en.wikipedia.org/wiki/Haversine_formula)
- **Usage**: Computing great-circle distance between geographical coordinates
- **Implementation**: `app/services/reco_service.py`
- **Formula**:
  ```
  a = sin²(Δφ/2) + cos(φ1) * cos(φ2) * sin²(Δλ/2)
  c = 2 * atan2(√a, √(1−a))
  d = R * c
  where φ is latitude, λ is longitude, R is earth's radius (6371 km)
  ```

#### **Exponential Decay** (Proximity Scoring)

- **Reference**: Standard exponential decay function
- **Usage**: Converting distance to proximity score
- **Formula**: `score = exp(-λ * distance)` where λ = 0.3

### Documentation Resources

#### **Markdown Guide**

- **Source**: [https://www.markdownguide.org/](https://www.markdownguide.org/)
- **Usage**: README and documentation formatting

#### **FastAPI Best Practices**

- **Source**: [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- **Usage**: Project structure and patterns

#### **SQLAlchemy Best Practices**

- **Source**: [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html)
- **Usage**: Query optimization and session management

### Deployment

#### **Render** (Hosting Platform)

- **Source**: [https://render.com/](https://render.com/)
- **Usage**: API deployment and hosting
- **Live URL**: [https://luna-backend-shkw.onrender.com/docs/](https://luna-backend-shkw.onrender.com/docs/)

### Learning Resources

The following resources informed architecture and algorithm design:

1. **Recommendation Systems**:

   - ["Recommender Systems Handbook"](https://link.springer.com/book/10.1007/978-1-0716-2197-4) - Concepts for feature-based recommendations
   - [Google's Recommendation Systems Course](https://developers.google.com/machine-learning/recommendation) - Feature engineering patterns

2. **FastAPI Architecture**:

   - [Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template) - Project structure inspiration

3. **Geospatial Computing**:
   - [Movable Type Scripts](https://www.movable-type.co.uk/scripts/latlong.html) - Haversine formula verification

### License Compliance

All dependencies are used in compliance with their respective open-source licenses:

- **MIT License**: FastAPI, SQLAlchemy, Pydantic, pytest, uvicorn
- **BSD License**: NumPy, scikit-learn, PostgreSQL
- **Apache 2.0**: uv

This project's use of these libraries falls under their permitted use cases for both commercial and non-commercial applications.

<br/>

## 13. Architecture Choices & Design Decisions

This section documents the key architectural decisions, trade-offs, and rationale behind the technical choices made in this project.

### 13.1 Overall Architecture Pattern

#### **Layered Architecture**

The project follows a **clean layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│         API Layer (FastAPI Routes)       │  ← HTTP endpoints, request/response
├─────────────────────────────────────────┤
│       Service Layer (Business Logic)     │  ← Recommendation, agent logic
├─────────────────────────────────────────┤
│      Data Access Layer (SQLAlchemy)      │  ← ORM models, database queries
├─────────────────────────────────────────┤
│          Database (PostgreSQL)           │  ← Persistent storage
└─────────────────────────────────────────┘
```

**Rationale**:

- **Maintainability**: Each layer has a single responsibility
- **Testability**: Business logic can be tested independently of HTTP layer
- **Flexibility**: Easy to swap implementations (e.g., change database, add caching)
- **Scalability**: Layers can be scaled independently in future microservices

**Trade-offs**:

- ✅ **Pros**: Clear boundaries, easy to understand, excellent for team collaboration
- ❌ **Cons**: More files and boilerplate, slight performance overhead from abstraction

### 13.2 Technology Choices

#### **FastAPI over Django/Flask**

**Decision**: Use FastAPI as the web framework

**Rationale**:

1. **Automatic API Documentation**: OpenAPI (Swagger) and ReDoc generated automatically
2. **Type Safety**: Native support for Python type hints with Pydantic validation
3. **Performance**: ASGI-based, async support, comparable to Node.js/Go
4. **Modern Python**: Uses Python 3.11+ features
5. **Developer Experience**: Excellent error messages, hot reload

**Trade-offs**:

- ✅ **Pros**: Fast, modern, excellent docs, type-safe
- ❌ **Cons**: Newer ecosystem than Django, fewer built-in features (no admin panel)

#### **SQLAlchemy 2.x over Django ORM**

**Decision**: Use SQLAlchemy as the ORM

**Rationale**:

1. **Framework Agnostic**: Not tied to Django
2. **Powerful Queries**: Complex joins and aggregations easier to express
3. **Migration Control**: Full control over schema evolution
4. **Performance**: Better query optimization capabilities
5. **Type Safety**: Works well with mypy and type checkers

**Trade-offs**:

- ✅ **Pros**: Powerful, flexible, works with any framework
- ❌ **Cons**: Steeper learning curve, more verbose than Django ORM

#### **PostgreSQL over NoSQL (MongoDB, etc.)**

**Decision**: Use PostgreSQL as the database

**Rationale**:

1. **Relational Data**: User-venue relationships, social graphs are naturally relational
2. **ACID Guarantees**: Important for bookings and plan confirmations
3. **Query Capabilities**: Complex joins needed for recommendations
4. **JSON Support**: PostgreSQL supports JSONB for flexible fields if needed
5. **Maturity**: Battle-tested, excellent tooling

**Trade-offs**:

- ✅ **Pros**: ACID, powerful queries, proven at scale
- ❌ **Cons**: Requires schema design upfront, scaling requires more effort than NoSQL

#### **uv over pip/poetry**

**Decision**: Use uv for package management

**Rationale**:

1. **Speed**: 10-100x faster than pip (written in Rust)
2. **Reliability**: Better dependency resolution
3. **Simplicity**: Single tool for virtual environments and packages
4. **Lock Files**: `uv.lock` ensures reproducible builds

**Trade-offs**:

- ✅ **Pros**: Very fast, modern, excellent UX
- ❌ **Cons**: Newer tool, smaller community than pip/poetry

### 13.3 Database Schema Design

#### **Normalized Schema with Separate Tables**

**Decision**: Use separate tables for Users, Venues, Interactions, Social Edges, Plans, Bookings

**Rationale**:

1. **Normalization**: Reduces data redundancy
2. **Integrity**: Foreign key constraints ensure referential integrity
3. **Flexibility**: Easy to add new interaction types or relationship types
4. **Query Efficiency**: Indexes on foreign keys enable fast joins

**Key Design Patterns**:

1. **UUID Primary Keys**:

   ```python
   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
   ```

   - **Why**: Distributed system friendly, no collision risk, obfuscates data size

2. **Timestamps on Everything**:

   ```python
   created_at = Column(DateTime(timezone=True), server_default=func.now())
   ```

   - **Why**: Essential for analytics, debugging, and compliance

3. **Interaction Type Enum**:

   ```python
   interaction_type = Column(String, nullable=False)  # "view", "interest", "like"
   ```

   - **Why**: Flexible for adding new types without schema migration
   - **Trade-off**: Could use DB enum for better type safety

4. **Denormalized Fields for Performance**:
   - Venue `rating` and `price_level` are stored directly (not computed)
   - User `home_lat`, `home_lng` stored redundantly for fast distance calculations
   - **Why**: Read-heavy workload, precompute for speed

### 13.4 Recommendation System Design

#### **Feature-Based Approach (Not End-to-End ML)**

**Decision**: Use hand-crafted features with weighted scoring instead of training a neural network

**Rationale**:

1. **Interpretability**: Can explain why a venue/person was recommended
2. **Cold Start**: Works immediately without training data
3. **Debuggability**: Easy to tune weights and observe effects
4. **ML-Ready**: Features are structured for easy transition to learned models

**Architecture**:

```python
venue_score = (
    0.4 * spatial_proximity +      # Distance-based
    0.4 * user_preference +        # Behavioral signals
    0.2 * global_popularity        # Social proof
)
```

**Weights Chosen**:

- **40% Spatial**: Geography is primary constraint (users won't travel far)
- **40% Preference**: Personal taste is equally important
- **20% Popularity**: Social proof matters but shouldn't dominate

**Why Not Deep Learning?**:

- ❌ Insufficient training data (only seed data)
- ❌ Overkill for MVP/prototype
- ✅ Can add later without API changes

**Trade-offs**:

- ✅ **Pros**: Simple, fast, interpretable, works immediately
- ❌ **Cons**: Suboptimal compared to learned weights, requires manual tuning

#### **Spatial Indexing Decision**

**Current**: Compute distance to all venues, then sort

**Alternative**: Use PostgreSQL PostGIS for spatial indexes

**Trade-off Analysis**:

- **Current Approach**:

  - ✅ Simple, no extra dependencies
  - ✅ Works fine for 10s-100s of venues
  - ❌ O(n) complexity for n venues

- **PostGIS Approach**:
  - ✅ O(log n) complexity with R-tree index
  - ✅ Scales to millions of venues
  - ❌ Extra dependency, more complex setup
  - ❌ Overkill for current scale

**Decision**: Start simple, migrate to PostGIS when venue count exceeds ~10,000

### 13.5 API Design Decisions

#### **RESTful Resource-Oriented Design**

**Decision**: Use RESTful conventions with resource-based URLs

**Examples**:

```
GET    /users/{user_id}                  # Get user
POST   /venues/{venue_id}/interactions   # Log interaction
GET    /reco/venues/{user_id}            # Get recommendations
POST   /plans/{plan_id}/confirm          # Confirm plan (agent trigger)
```

**Rationale**:

1. **Predictability**: Standard patterns are easy to understand
2. **Tooling**: Works with OpenAPI, Postman, etc.
3. **Caching**: GET requests are cacheable
4. **Idempotency**: POST for creation, PUT for updates

**Non-RESTful Exceptions**:

- `/reco/venues/{user_id}` could be `/users/{user_id}/venue-recommendations`
- **Decision**: Shorter URLs, recommendations are a distinct concern

#### **Response Format**

**Decision**: Return JSON with flat structures, no hypermedia (HATEOAS)

**Example**:

```json
{
  "venue_id": "uuid",
  "score": 0.87,
  "distance_km": 1.2
}
```

**Rationale**:

- **Simplicity**: Easy for clients to parse
- **Performance**: Smaller payloads
- **Flexibility**: Frontend controls navigation

**Trade-offs**:

- ✅ **Pros**: Simple, fast, mobile-friendly
- ❌ **Cons**: Clients need to construct URLs, no self-documentation

### 13.6 Testing Strategy

#### **In-Memory SQLite for Tests**

**Decision**: Use SQLite in-memory database for tests instead of PostgreSQL

**Rationale**:

1. **Speed**: Tests run in milliseconds
2. **Isolation**: Each test gets a fresh database
3. **CI/CD**: No need to provision PostgreSQL in CI
4. **Simplicity**: No cleanup needed

**Implementation**:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
```

**Trade-offs**:

- ✅ **Pros**: Fast, simple, reproducible
- ❌ **Cons**: Doesn't test PostgreSQL-specific features (JSONB, etc.)

**Risk Mitigation**: Manual testing against Supabase before deployment

#### **Fixture-Based Testing**

**Decision**: Use pytest fixtures for database and client setup

**Example**:

```python
@pytest.fixture
def db_session():
    # Fresh database for each test
    yield session

@pytest.fixture
def client(db_session):
    # API client with test database
    yield TestClient(app)
```

**Rationale**:

- **DRY**: Setup code in one place
- **Isolation**: Each test is independent
- **Composition**: Fixtures can depend on other fixtures

### 13.7 Agent/Booking Flow Design

#### **Synchronous Agent (Not Async Queue)**

**Decision**: Agent runs synchronously when plan is confirmed

**Current Flow**:

```
Client → POST /plans/{id}/confirm → create_booking_for_plan() → Response
```

**Alternative** (with message queue):

```
Client → POST /plans/{id}/confirm → Queue Job → Worker → create_booking_for_plan()
```

**Rationale for Synchronous**:

- ✅ Simpler: No queue infrastructure needed
- ✅ Immediate feedback: User knows booking status instantly
- ✅ Easier debugging: Stack traces are visible

**Trade-offs**:

- ✅ **Pros**: Simple, immediate, easy to debug
- ❌ **Cons**: Doesn't scale to long-running external API calls

**Future Migration Path**: When integrating real booking APIs (OpenTable, etc.), switch to async queue (Celery, Redis Queue, etc.)

### 13.8 Configuration Management

#### **Pydantic Settings with .env**

**Decision**: Use Pydantic Settings with `.env` file

**Implementation**:

```python
class Settings(BaseSettings):
    database_url: PostgresDsn

    class Config:
        env_file = ".env"

settings = Settings()
```

**Rationale**:

1. **Type Safety**: Database URL is validated as PostgreSQL DSN
2. **Environment Parity**: Same code works in dev/staging/prod
3. **Security**: `.env` is gitignored, secrets stay out of code
4. **Validation**: Pydantic catches misconfigurations at startup

**Trade-offs**:

- ✅ **Pros**: Type-safe, validates at startup, 12-factor compliant
- ❌ **Cons**: Requires `.env` file locally (documented in README)

### 13.9 Error Handling

#### **FastAPI Exception Handlers**

**Decision**: Let FastAPI handle most exceptions, custom handlers for business logic

**Current Approach**:

- HTTP 404 for missing resources (automatic via `get_or_404` pattern)
- HTTP 422 for validation errors (automatic via Pydantic)
- HTTP 500 for unexpected errors (automatic)

**Custom Handling**:

- Plan confirmation failures return meaningful error messages
- Recommendation service returns empty list instead of error if user has no data

**Trade-offs**:

- ✅ **Pros**: Consistent error format, good developer experience
- ❌ **Cons**: Could add more detailed error codes for client-side handling

### 13.10 Deployment Architecture

#### **Single Server Deployment (Render)**

**Current Setup**:

```
                    ┌──────────────────┐
Internet ──────────►│   Render.com     │
                    │  (Single Server) │
                    │                  │
                    │  Uvicorn (ASGI)  │
                    │       │          │
                    │   FastAPI App    │
                    │       │          │
                    │   SQLAlchemy     │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │    Supabase      │
                    │   (PostgreSQL)   │
                    └──────────────────┘
```

**Rationale**:

- ✅ Simple: One service to deploy and monitor
- ✅ Cost-effective: Free tier on Render, Supabase
- ✅ Sufficient: Handles prototype/MVP traffic

**Future Scaling Path**:

```
                    ┌──────────────────┐
                    │   Load Balancer  │
                    └────────┬─────────┘
                     ┌───────┼────────┐
              ┌──────▼─┐  ┌──▼──────┐ │
              │ API    │  │ API     │ │ ...
              │ Server │  │ Server  │ │
              └────┬───┘  └───┬─────┘ │
                   └──────────┼───────┘
                     ┌────────▼─────────┐
                     │  Redis (Cache)   │
                     └──────────────────┘
                     ┌────────▼─────────┐
                     │ PostgreSQL       │
                     │ (Read Replicas)  │
                     └──────────────────┘
```

### 13.11 Key Design Principles

Throughout this project, the following principles guided decision-making:

1. **Start Simple, Migrate Gradually**

   - SQLite for tests → PostgreSQL for production
   - Heuristic recommendations → ML models later
   - Synchronous agent → Async queue when needed

2. **Make It Work, Then Make It Fast**

   - Focus on correctness first
   - Optimize only with profiling data
   - Current performance is acceptable for scale

3. **Optimize for Developer Experience**

   - Type hints everywhere for IDE support
   - Automatic API docs via FastAPI
   - Clear separation of concerns

4. **Prepare for Production Without Over-Engineering**
   - Database migrations via SQLAlchemy
   - Environment-based configuration
   - Comprehensive test suite
   - But: No premature optimization, no unnecessary complexity

### 13.12 What Was NOT Done (Intentionally)

To maintain simplicity and focus, the following were intentionally omitted:

1. **Authentication/Authorization**: Endpoints are public

   - **Why**: Focus on core recommendation logic
   - **When to add**: Before production launch

2. **Caching Layer (Redis)**: No caching of recommendations

   - **Why**: Premature optimization
   - **When to add**: When response times exceed 100ms

3. **Monitoring/Observability**: No logging, metrics, tracing

   - **Why**: MVP phase
   - **When to add**: Before production with tools like Datadog, Sentry

4. **Containerization (Docker)**: No Dockerfile
   - **Why**: Render handles deployment
   - **When to add**: For local development consistency or K8s deployment

These decisions keep the codebase lean while maintaining a clear migration path for each feature when needed.

<br/>

## 14. Future Improvements

Some obvious next steps:

- Evaluation:
  - Offline evaluation with held-out data.
  - A/B tests for different scoring formulations.
- Productization:

  - Caching of top recommendations per user.
  - Background jobs to periodically recompute candidate sets.
  - Monitoring (logging, metrics, tracing) for recommendation performance.

- Product features:
- Hard constraints (budget, maximum travel time).
- Personalized “moods” or “vibes” (chill, loud, romantic) learned from past behavior.
