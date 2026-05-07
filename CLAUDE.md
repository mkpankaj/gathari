# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Gathari is an MVP stock-analysis web app for the Indian Nifty50 universe (30 tickers). Built for a small group of users. Simplicity, stability, and free hosting trump completeness or scale. `docs/plan.md` is the locked single source of truth — do not add features or architecture not in it.

## Development commands

All backend commands run from `backend/` with the venv activated.

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Run dev server
uvicorn app.main:app --reload
# → http://localhost:8000/api/health

# DB migrations
alembic revision --autogenerate -m "describe change"
alembic upgrade head

# Seed Nifty50 stocks (run once after first migration)
python -m app.seed.seed
```

Frontend not yet created. When it exists: `npm run dev` from `frontend/`.

## Architecture

```
[React SPA on Render]  ──HTTPS──>  [FastAPI on Render]  ──>  [Postgres on Neon]
                                          │
                                          ├──> yfinance → Yahoo Finance
                                          └──> feedparser → Google News RSS
```

Synchronous request/response only. No queue, no background scheduler, no Redis.

### Backend module layout

```
backend/app/
  main.py        — FastAPI app, CORS middleware, router registration
  config.py      — Settings loaded from .env via pydantic-settings
  db.py          — SQLAlchemy async engine + session factory
  models.py      — ORM entities (User, Stock, StockPrice, Nifty50Index, Nifty50Meta, Headline)
  schemas.py     — Pydantic request/response models
  deps.py        — get_db, get_current_user dependency injectors
  auth/          — POST /api/auth/register, POST /api/auth/login; JWT + bcrypt
  seed/          — Bootstrap 30 Nifty50 tickers + yfinance industry fetch
  stocks/        — routes.py, fetcher.py (yfinance), analyzer.py (trend labels)
  nifty/         — routes.py, fetcher.py (index series)
  news/          — routes.py, fetcher.py (Google News RSS via feedparser)
  refresh/       — POST /api/refresh — orchestrates stocks → index → news sequentially
```

### REST API

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/register` | Create user |
| POST | `/api/auth/login` | Return 7-day JWT |
| GET | `/api/health` | Health check |
| GET | `/api/dashboard?timeline=2Y` | Trend analysis table for all stocks |
| GET | `/api/stocks/{symbol}?timeline=2Y` | Aggregated price series + headlines |
| GET | `/api/nifty50?timeline=2Y` | Index series |
| POST | `/api/refresh` | Fetch new data; returns per-stock status |

### Key data flows

**Refresh** — sequential, partial-save on failure. For each stock: if `last_fetch_date == today` skip; otherwise yfinance download since last fetch date, upsert into `stock_prices`, update `last_fetch_date`. News refetched only if `last_fetch_date_news` is NULL or > 30 days old; news failures are non-fatal.

**Trend labels** — linear regression (`numpy`) on close prices over the selected timeline window:
```
slope_pct = linregress(days, close).slope / mean(close) * 100   # %/day
delta_pct = (close[-1] - close[0]) / close[0] * 100
```
Five labels: Strong Upward, Weak Upward, Strong Downward, Weak Downward, Neutral. Thresholds live as constants in `app/stocks/analyzer.py`.

**Aggregation** (stock chart buckets):
- 1M → daily | 3M, 6M → weekly mean | 9M, 1Y, 1.5Y, 2Y → monthly mean

**Auth** — bcrypt password hash, HS256 JWT (7-day expiry). Token passed as `Authorization: Bearer <token>`. Frontend stores token in `localStorage`.

### Frontend screens (when built)

Plain JavaScript (no TypeScript). Routes: `/login`, `/register`, `/dashboard`, `/nifty50`, `/stocks/:symbol`. Shared: `<Toast />`, `<TimelineTabs />`, `<TrendBadge />`, `<ProtectedRoute />`. Axios interceptor injects auth header.

## Environment variables

Set in `backend/.env` (copy from `.env.example`):
- `DATABASE_URL` — Neon Postgres connection string
- `JWT_SECRET` — long random string
- `CORS_ORIGINS` — comma-separated allowed origins
- `JWT_ALGORITHM` — default HS256
- `JWT_EXPIRE_DAYS` — default 7

Same Neon DB is used for both local dev and production.

## Deployment

| Layer | Provider | Start command |
|-------|----------|---------------|
| Backend | Render Web Service (free) | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Frontend | Render Static Site (free) | `npm run build`, publish dir `dist`, env `VITE_API_BASE_URL` |
| DB | Neon (free) | Shared with local dev; auto-suspends |

Migrations run automatically on backend startup. No Docker.

## Locked scope — do not add

Configuration page, background scheduler, password reset, admin UI, rate limiting, caching layer, E2E tests (pytest only for analyzer + auth), NewsAPI fallback, TypeScript on frontend.

## Build order (current status)

1. ✅ Backend skeleton + Postgres + Alembic + Nifty50 seed
2. ✅ Auth (register, login, JWT)
3. 🔲 Stock fetcher + `/refresh` endpoint
4. 🔲 Analyzer + `/dashboard`
5. 🔲 Stock detail + Nifty50 endpoints
6. 🔲 News fetcher
7. 🔲 Frontend: login → dashboard → stock → nifty50
8. 🔲 Deploy to Render + Neon
9. 🔲 Smoke test, hand off to small group
