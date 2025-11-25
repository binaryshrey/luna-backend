# Test Suite for Luna Backend

This directory contains the test suite for the Luna Backend API service.

## Overview

The test suite uses:

- **pytest** - Testing framework
- **httpx** - HTTP client for testing FastAPI endpoints
- **SQLite in-memory database** - For isolated, fast test execution

## Running Tests

### Run all tests

```
uv run pytest
```

### Run with verbose output

```
uv run pytest -v
```

### Run specific test file

```
uv run pytest tests/test_users.py
```

### Run specific test

```
uv run pytest tests/test_users.py::test_create_user
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Test configuration and fixtures
├── test_health.py       # Health check endpoint tests
├── test_users.py        # User API endpoint tests
└── test_venues.py       # Venue API endpoint tests
```

## Test Coverage

### Health API (`test_health.py`)

- Health check endpoint returns correct status
- Health check response structure validation

### Users API (`test_users.py`)

- Create user with full data
- Create user with minimal required fields
- Duplicate handle validation
- List users (empty and populated)

### Venues API (`test_venues.py`)

- Create venue with full data
- Create venue with minimal required fields
- List venues (empty and populated)

## Fixtures

### `db_session`

Provides a fresh SQLite in-memory database session for each test. The database is automatically created and torn down for each test function.

### `client`

Provides a FastAPI TestClient with the database dependency overridden to use the test database session.

## Notes

- **Database**: Tests use SQLite in-memory database for speed and isolation
- **Test Isolation**: Each test runs with a fresh database to ensure test independence
- **Production vs Test**: The application uses PostgreSQL in production, but tests use SQLite for simplicity

## Adding New Tests

1. Create a new test file in the `tests/` directory (e.g., `test_plans.py`)
2. Import necessary fixtures and modules:
   ```python
   def test_my_feature(client):
       response = client.get("/my-endpoint/")
       assert response.status_code == 200
   ```
3. Use the `client` fixture to make requests to your API
4. Add assertions to verify expected behavior

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They are fast, isolated, and don't require external dependencies.

## Future Improvements

- Add tests for recommendations API
- Add tests for plans API
- Add integration tests with PostgreSQL
- Add performance/load tests
- Add test coverage reporting
