# Luna Backend - Architecture Diagrams

This document provides visual representations of the system architecture.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Mobile App, Web Browser, API Consumers)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      API Gateway / CDN                           │
│                        (Render.com)                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                       FastAPI Application                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              API Layer (Routes)                         │   │
│  │  /users  /venues  /reco  /plans  /health               │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐   │
│  │            Service Layer                                │   │
│  │                                                          │   │
│  │  ┌──────────────────┐    ┌──────────────────┐          │   │
│  │  │ Recommendation   │    │  Agent Service   │          │   │
│  │  │    Service       │    │   (Bookings)     │          │   │
│  │  └──────────────────┘    └──────────────────┘          │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐   │
│  │         Data Access Layer (SQLAlchemy ORM)              │   │
│  │  Models: User, Venue, Interaction, Social, Plan, etc.  │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            │ PostgreSQL Protocol
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                    Database Layer                                 │
│                   (Supabase PostgreSQL)                          │
│                                                                  │
│  Tables: users, venues, user_venue_interactions,                │
│          user_social_edges, plans, plan_participants, bookings  │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow - Venue Recommendation

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │ 1. GET /reco/venues/{user_id}
     ▼
┌─────────────────┐
│   API Router    │
│   (reco.py)     │
└────┬────────────┘
     │
     │ 2. Call recommend_venues_for_user()
     ▼
┌──────────────────────────────────────────────────────┐
│         Recommendation Service                        │
│        (reco_service.py)                             │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │ Step 1: Fetch User Data                     │    │
│  │  - home_lat, home_lng                       │    │
│  └───────────────┬─────────────────────────────┘    │
│                  │                                    │
│  ┌───────────────▼─────────────────────────────┐    │
│  │ Step 2: Fetch All Venues                    │    │
│  │  - lat, lng, category, rating               │    │
│  └───────────────┬─────────────────────────────┘    │
│                  │                                    │
│  ┌───────────────▼─────────────────────────────┐    │
│  │ Step 3: Fetch User Interactions             │    │
│  │  - likes, views, dwell_time                 │    │
│  └───────────────┬─────────────────────────────┘    │
│                  │                                    │
│  ┌───────────────▼─────────────────────────────┐    │
│  │ Step 4: Feature Engineering                 │    │
│  │  - Spatial Score (haversine distance)       │    │
│  │  - Preference Score (likes + dwell)         │    │
│  │  - Popularity Score (global likes)          │    │
│  └───────────────┬─────────────────────────────┘    │
│                  │                                    │
│  ┌───────────────▼─────────────────────────────┐    │
│  │ Step 5: Score Combination                   │    │
│  │  score = 0.4*spatial + 0.4*pref + 0.2*pop   │    │
│  └───────────────┬─────────────────────────────┘    │
│                  │                                    │
│  ┌───────────────▼─────────────────────────────┐    │
│  │ Step 6: Sort & Return Top-K                 │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────┬────────────────────────────────┘
                      │
                      │ 3. Return VenueReco[]
                      ▼
                 ┌─────────┐
                 │  Client │
                 └─────────┘
```

## Data Flow - Plan Confirmation & Booking

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │ 1. POST /plans/{plan_id}/confirm
     ▼
┌─────────────────┐
│   API Router    │
│   (plans.py)    │
└────┬────────────┘
     │
     │ 2. Fetch Plan from DB
     ▼
┌──────────────────┐
│   Database       │  ← Plan Details
│   (Read)         │
└────┬─────────────┘
     │
     │ 3. Validate Plan (exists, not already confirmed)
     ▼
┌──────────────────────────┐
│   Agent Service          │
│  (agent_service.py)      │
│                          │
│  create_booking_for_plan()│
│                          │
│  - Generate mock ref     │
│  - Create Booking record │
└────┬─────────────────────┘
     │
     │ 4. Insert Booking
     ▼
┌──────────────────┐
│   Database       │
│   (Write)        │
│                  │
│  bookings table  │
└────┬─────────────┘
     │
     │ 5. Update Plan status
     ▼
┌──────────────────┐
│   Database       │
│   (Update)       │
│                  │
│  plans table     │
└────┬─────────────┘
     │
     │ 6. Return confirmation
     ▼
┌─────────┐
│  Client │
└─────────┘
```

## Database Schema (Entity Relationship)

```
┌─────────────────────┐
│       User          │
│─────────────────────│
│ id (UUID) PK        │
│ handle              │
│ name                │
│ age                 │
│ home_lat            │
│ home_lng            │
│ created_at          │
└──────┬──────────────┘
       │
       │ 1:N
       │
       ├──────────────────────────────────────┐
       │                                      │
       │                                      │
┌──────▼──────────────┐              ┌───────▼────────────┐
│ UserVenueInteraction│              │ UserSocialEdge     │
│─────────────────────│              │────────────────────│
│ id (UUID) PK        │              │ id (UUID) PK       │
│ user_id FK ────┐    │              │ user_id FK         │
│ venue_id FK    │    │              │ other_user_id FK   │
│ interaction_type│    │              │ relationship_type  │
│ dwell_time      │    │              │ strength           │
│ created_at      │    │              │ created_at         │
└─────────────────┘    │              └────────────────────┘
                       │
                       │
                   ┌───▼──────────────┐
                   │      Venue        │
                   │───────────────────│
                   │ id (UUID) PK      │
                   │ name              │
                   │ description       │
                   │ category          │
                   │ lat               │
                   │ lng               │
                   │ price_level       │
                   │ rating            │
                   │ created_at        │
                   └───┬───────────────┘
                       │
                       │ 1:N
                       │
                   ┌───▼───────────────┐
                   │      Plan         │
                   │───────────────────│
                   │ id (UUID) PK      │
                   │ organizer_id FK   │
                   │ venue_id FK       │
                   │ start_time        │
                   │ status            │
                   │ created_at        │
                   └───┬───────────────┘
                       │
                       │ 1:N
                       │
              ┌────────┴────────┐
              │                 │
     ┌────────▼──────────┐  ┌──▼────────────┐
     │ PlanParticipant   │  │   Booking     │
     │───────────────────│  │───────────────│
     │ id (UUID) PK      │  │ id (UUID) PK  │
     │ plan_id FK        │  │ plan_id FK    │
     │ user_id FK        │  │ provider      │
     │ status            │  │ external_ref  │
     │ created_at        │  │ status        │
     └───────────────────┘  │ created_at    │
                            └───────────────┘
```

## Recommendation Algorithm Flow

### Venue Scoring Formula

```
For each venue v, compute:

spatial_score = exp(-0.3 * distance_km)
                ↓
           (distance-based decay)

preference_score = min(1.0, like_count * 0.5 + view_time / 300)
                    ↓
              (user's past interactions)

popularity_score = venue_like_count / max_likes_any_venue
                    ↓
              (global popularity)

final_score = 0.4 * spatial_score
            + 0.4 * preference_score
            + 0.2 * popularity_score

Sort by final_score descending → Return top K
```

### People (Companion) Scoring Formula

```
For each friend f and optional venue v:

base_strength = social_edge.strength
                 ↓
           (how close they are)

direct_pref = min(1.0, friend_likes_venue * 0.5 + friend_views / 300)
               ↓
         (friend's interest in specific venue)

category_pref = min(1.0, friend_likes_category * 0.3 + cat_views / 600)
                 ↓
           (friend's interest in venue category)

final_score = 0.6 * base_strength
            + 0.25 * direct_pref
            + 0.15 * category_pref

Sort by final_score descending → Return top K
```

## Technology Stack Layers

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                    │
│  FastAPI Swagger UI (/docs), ReDoc (/redoc)            │
│  OpenAPI Schema                                         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Application Layer                     │
│  Language: Python 3.11+                                 │
│  Framework: FastAPI 0.121.3+                            │
│  Server: Uvicorn (ASGI)                                 │
│  Validation: Pydantic 2.x                               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Business Logic Layer                  │
│  Services: reco_service.py, agent_service.py            │
│  ML/Features: numpy, scikit-learn                       │
│  Algorithms: Haversine, Weighted Scoring                │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Data Access Layer                     │
│  ORM: SQLAlchemy 2.0.44+                                │
│  Driver: psycopg2-binary                                │
│  Models: User, Venue, Interaction, etc.                 │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Persistence Layer                     │
│  Database: PostgreSQL 14+                               │
│  Hosting: Supabase                                      │
│  Schema Management: SQLAlchemy create_all()             │
└─────────────────────────────────────────────────────────┘
```

## Testing Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Test Suite                           │
│                  (pytest 8.0+)                          │
└────────────────────────┬────────────────────────────────┘
                         │
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼─────┐  ┌──────▼─────┐
│ test_users   │  │test_venues │  │test_health │
└───────┬──────┘  └──────┬─────┘  └──────┬─────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                ┌────────▼────────┐
                │  conftest.py    │
                │   (Fixtures)    │
                └────────┬────────┘
                         │
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼─────┐  ┌──────▼─────┐
│ db_session   │  │   client   │  │  FastAPI   │
│  fixture     │  │  fixture   │  │ TestClient │
└───────┬──────┘  └──────┬─────┘  └──────┬─────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                ┌────────▼────────┐
                │  SQLite :memory:│
                │  (Test Database)│
                └─────────────────┘
```

## Deployment Flow

```
┌─────────────────┐
│ Local Dev       │
│ (Developer)     │
└────────┬────────┘
         │
         │ git push
         ▼
┌─────────────────┐
│ GitHub          │
│ (Repository)    │
└────────┬────────┘
         │
         │ webhook
         ▼
┌─────────────────┐
│ Render.com      │
│ (CI/CD)         │
│                 │
│ 1. Pull code    │
│ 2. uv install   │
│ 3. Run tests    │
│ 4. Start server │
└────────┬────────┘
         │
         │ deployed
         ▼
┌─────────────────────────────────────┐
│ Production Environment              │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Uvicorn ASGI Server          │  │
│  │ (Running FastAPI App)        │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│               │ PostgreSQL Protocol │
│               ▼                     │
│  ┌──────────────────────────────┐  │
│  │ Supabase PostgreSQL          │  │
│  │ (Managed Database)           │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
         │
         │ HTTPS
         ▼
┌─────────────────┐
│ End Users       │
└─────────────────┘
```
