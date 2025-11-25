# Luna Backend – Track 2

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
1. High-Level Overview
2. Architecture
3. Local Setup
4. DB (Supabase) Setup
5. Seeding the DB
6. Running the Server + Deployment
7. API Overview
8. Recommendation Algorithms & ML Design
9. Agent / Booking Flow
10. Test Suite
11. Future Improvements

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
### 3.1 Prerequisites

- Python 3.11+
- uv
- A Supabase project (or any Postgres instance)


### 3.2 Clone the Repository
```
git clone https://github.com/binaryshrey/luna-backend.git
cd luna-backend
```

### 3.3 Environment & Dependencies (with uv)

Create and sync the virtual environment:

Create local virtualenv in .venv/ 
```
uv venv .venv
```

Activate it
```
source .venv/bin/activate
```

Install all dependencies from pyproject.toml 
```
uv sync --active
```


Key dependencies (from pyproject.toml):
- fastapi
- uvicorn[standard]
- sqlalchemy
- psycopg2-binary
- pydantic
- python-dotenv
- numpy
- scikit-learn
- typing-extensions


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

![Live](https://raw.githubusercontent.com/binaryshrey/luna-backend/refs/heads/main/res/live.png)

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
score = 0.6 * base_strength

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

## 11. Future Improvements

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

