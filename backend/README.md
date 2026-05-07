# Gathari Backend

FastAPI service for the Gathari MVP. See `../docs/plan.md` for full architecture.

## Local dev

Prereqs: Python 3.12. No Docker needed — the app uses Neon (cloud Postgres) for both local dev and production.

```powershell
# 1. Create and activate virtualenv
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configure env
copy .env.example .env
# Edit .env: fill in DATABASE_URL from Neon dashboard, set JWT_SECRET to any long random string

# 3. Run migrations + seed
alembic upgrade head
python -m app.seed.seed

# 4. Run API
uvicorn app.main:app --reload
# → http://localhost:8000/api/health
```

## Migrations

```powershell
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Deploy (Render)

1. Create a **Web Service** on Render pointing to the `backend/` directory.
2. Build command: `pip install -r requirements.txt`
3. Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment variables: `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`
