# Quick Start Guide - Luna Backend

This guide will get you up and running with the Luna Backend in 5 minutes.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.11 or higher installed
- [ ] `uv` package manager installed
- [ ] Git installed
- [ ] A Supabase account (free tier is fine)
- [ ] Terminal/command line access

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/binaryshrey/luna-backend.git
cd luna-backend
```

### 2. Install uv (if not already installed)

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Using pip:**

```bash
pip install uv
```

### 3. Create Virtual Environment

```bash
uv venv .venv
```

### 4. Activate Virtual Environment

**macOS/Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
uv sync --active
```

### 6. Set Up Database

#### Option A: Using Supabase (Recommended)

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Create a new project
3. Navigate to **Project Settings → Database**
4. Copy the connection string under **Connection string → URI**

#### Option B: Local PostgreSQL

If you have PostgreSQL running locally:

```
postgresql+psycopg2://username:password@localhost:5432/luna_db
```

### 7. Configure Environment Variables

Create a `.env` file:

```bash
touch .env
```

Add your database URL:

```env
DATABASE_URL=postgresql+psycopg2://[YOUR_USER]:[YOUR_PASSWORD]@[YOUR_HOST]:5432/[YOUR_DATABASE]
```

**Example:**

```env
DATABASE_URL=postgresql+psycopg2://postgres.abc123:yourpassword@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

### 8. Seed the Database

This creates tables and populates them with sample data:

```bash
uv run python -m app.seed
```

You should see:

```
✅ Seed data inserted: 24 users, 20 venues, XXX interactions, YYY social edges, 5 plans.
```

### 9. Start the Server

```bash
uv run uvicorn app.main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 10. Test the API

Open your browser and visit:

- **API Docs (Swagger)**: http://127.0.0.1:8000/docs
- **Alternative Docs (ReDoc)**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health/

## Quick API Tests

### Test 1: List Users

```bash
curl http://127.0.0.1:8000/users/
```

### Test 2: Get Venue Recommendations

First, get a user ID from the users list, then:

```bash
curl http://127.0.0.1:8000/reco/venues/{user_id}?limit=5
```

### Test 3: Create a New User

```bash
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "handle": "testuser",
    "name": "Test User",
    "age": 25,
    "home_lat": 40.7128,
    "home_lng": -74.0060
  }'
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_users.py

# Run specific test
uv run pytest tests/test_users.py::test_create_user
```

## Common Issues & Solutions

### Issue: "No module named 'app'"

**Solution:** Make sure you're in the project root directory and the virtual environment is activated.

```bash
# Check current directory
pwd

# Should show: /path/to/luna-backend

# Activate environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Issue: "Database connection failed"

**Solution:** Check your `.env` file:

1. Verify `DATABASE_URL` is set correctly
2. Ensure your Supabase project is running
3. Check that your IP is allowed (Supabase → Settings → Database → Connection pooling)
4. Test connection string format:
   ```
   postgresql+psycopg2://USER:PASSWORD@HOST:5432/DATABASE
   ```

### Issue: "Port 8000 already in use"

**Solution:** Either kill the existing process or use a different port:

```bash
# Use different port
uv run uvicorn app.main:app --reload --port 8001

# Or find and kill the process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "uv: command not found"

**Solution:** Install uv:

```bash
# Using pip
pip install uv

# Or using curl (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then restart your terminal or source your shell config
source ~/.bashrc  # or ~/.zshrc
```

### Issue: Seed script says "tables already exist"

**Solution:** This is normal if you've run the seed script before. The script is idempotent and won't duplicate data.

If you want to start fresh:

1. Go to Supabase → Database → Tables
2. Delete all tables
3. Run the seed script again

## Next Steps

Now that you're set up:

1. Read the full [README.md](./README.md) for detailed documentation
2. Explore [ARCHITECTURE.md](./ARCHITECTURE.md) for system design details
3. Check out [tests/README.md](./tests/README.md) for testing documentation
4. Try the live demo: [https://luna-backend-shkw.onrender.com/docs/](https://luna-backend-shkw.onrender.com/docs/)

## Key Endpoints Reference

| Method | Endpoint                    | Description                     |
| ------ | --------------------------- | ------------------------------- |
| GET    | `/health/`                  | Health check                    |
| GET    | `/users/`                   | List all users                  |
| GET    | `/users/{id}`               | Get specific user               |
| POST   | `/users/`                   | Create new user                 |
| GET    | `/venues/`                  | List all venues                 |
| GET    | `/venues/{id}`              | Get specific venue              |
| POST   | `/venues/`                  | Create new venue                |
| POST   | `/venues/{id}/interactions` | Log user interaction            |
| GET    | `/reco/venues/{user_id}`    | Get venue recommendations       |
| GET    | `/reco/people/{user_id}`    | Get people recommendations      |
| POST   | `/plans/`                   | Create a plan                   |
| POST   | `/plans/{id}/confirm`       | Confirm plan (triggers booking) |

## Development Workflow

```bash
# 1. Make changes to code
vim app/api/users.py

# 2. Server auto-reloads (if using --reload flag)
# Check http://127.0.0.1:8000/docs

# 3. Run tests
uv run pytest

# 4. Check for errors
uv run pytest tests/test_users.py -v

# 5. Commit changes
git add .
git commit -m "Add feature X"
git push
```

## Environment Variables Reference

Create a `.env` file with these variables:

```env
# Required
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db

```

## Resources

- **Documentation**: [README.md](./README.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Live API**: https://luna-backend-shkw.onrender.com/docs/
- **Repository**: https://github.com/binaryshrey/luna-backend
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Supabase Docs**: https://supabase.com/docs
