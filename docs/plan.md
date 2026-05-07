# Gathari — MVP Implementation Plan

Locked plan, single source of truth. Generated 2026-05-06 after requirements review.

## Goal
MVP / POC of a stock analysis web app for the Indian Nifty50 universe. Must be deployed publicly, used by a small group, with very small data. Stack must be simple, free/open-source, stable, easy to maintain.

## Decisions locked

| Topic | Decision |
|-------|----------|
| Login identity | User Id + Password |
| Universe | Nifty50 — seeded from `docs/nifty50-stocks.md` (30 tickers for MVP) |
| Refresh trigger | Manual button only (no scheduler) |
| Default analysis window | 2 years |
| Configuration page | Dropped |
| News source | Google News RSS only (no NewsAPI) |
| News fetch cadence | Per-stock; refetch only if `last_fetch_date_news` older than 30 days |
| News failure | Non-fatal — show analysis without news |
| Stock data source | `yfinance` Python library |
| Search scope | Nifty50 universe only |
| Refresh scope | All Nifty50 stocks + Nifty50 index, sequential, partial-save on failure |
| JWT expiry | 7 days |
| Password storage | bcrypt + JWT in `Authorization: Bearer` |
| Industry source | `yfinance .info['industry']`, fetched at seed time |

## Architecture

```
[React SPA on Vercel]  ──HTTPS──>  [FastAPI on Render]  ──>  [Postgres on Neon]
                                          │
                                          ├──> yfinance → Yahoo Finance
                                          └──> feedparser → Google News RSS
```

Synchronous request/response. No queue, no background scheduler, no Redis.

## Tech stack (locked)

| Layer | Choice |
|-------|--------|
| Frontend | React 18 + Vite, Tailwind CSS, Recharts, Axios, React Router — **plain JavaScript** |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2 |
| DB | Postgres 15 (Neon free tier) — used for both local dev and production |
| Stock data | `yfinance` |
| News | `feedparser` against `news.google.com/rss/search` |
| Auth | `passlib[bcrypt]` + `python-jose` (JWT) |
| Analysis | `numpy` (linear regression), `pandas` (aggregation) |
| Hosting | Render Static Site (FE) + Render Web Service (BE) + Neon (DB) — no Docker |

## DB schema

```sql
users
  id           uuid pk
  user_id      text unique not null
  user_name    text not null
  password_hash text not null
  created_at   timestamptz default now()

stocks
  symbol                  text pk          -- "RELIANCE.NS"
  name                    text not null
  industry                text
  last_fetch_date         date
  last_fetch_date_news    date

stock_prices
  symbol       text fk -> stocks.symbol
  trade_date   date
  open, high, low, close   numeric
  volume       bigint
  primary key (symbol, trade_date)

nifty50_index
  trade_date   date pk
  open, high, low, close   numeric

nifty50_meta
  id smallint pk default 1 check (id = 1)
  last_fetch_date  date

headlines
  id           bigserial pk
  symbol       text fk -> stocks.symbol
  headline     text
  url          text
  source       text
  published_at timestamptz
  fetched_at   timestamptz default now()
  unique (symbol, url)
```

Indexes:
- `stock_prices(symbol, trade_date desc)`
- `headlines(symbol, published_at desc)`

## REST endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/register` | Create user |
| POST | `/api/auth/login` | Return JWT (7-day expiry) |
| GET | `/api/dashboard?timeline=2Y` | Analysis table for all stocks |
| GET | `/api/stocks/{symbol}?timeline=2Y` | Aggregated price series + cached headlines |
| GET | `/api/nifty50?timeline=2Y` | Index series |
| POST | `/api/refresh` | Orchestrate: stocks → index → news; returns per-stock status |

## Refresh flow (sequential, partial-save)

```
For each stock in stocks:
   if last_fetch_date == today: skip
   start = last_fetch_date + 1 day  (or today - 1y if NULL)
   try:
       df = yfinance.download(symbol, start, today)
       upsert df rows into stock_prices
       update stocks.last_fetch_date = today
   except: log; continue
   if last_fetch_date_news is NULL or older than 30 days:
       try Google News RSS fetch → upsert headlines, update last_fetch_date_news
       except: log; continue
Fetch Nifty50 index via same incremental logic
Return JSON: { perStock: [...], index: {...} }
```

## Trend label logic

```
slope_pct = linregress(days, close).slope / mean(close) * 100   # %/day
delta_pct = (close[-1] - close[0]) / close[0] * 100

if slope_pct > 0  and delta_pct > 5:                "Strong Upward"
elif abs(slope_pct) <= 0.05 and 0 < delta_pct < 3:  "Weak Upward"
elif slope_pct < 0 and delta_pct < -5:              "Strong Downward"
elif slope_pct < 0 and -3 < delta_pct < 0:          "Weak Downward"
else:                                                "Neutral"
```

Thresholds live in `app/stocks/analyzer.py` constants — easy to tune.

## Aggregation (Stock page chart)

| Timeline | Bucket |
|----------|--------|
| 1M | daily |
| 3M, 6M | weekly mean |
| 9M, 1Y, 1.5Y, 2Y | monthly mean |

## Frontend screens

| Route | Page |
|-------|------|
| `/login` | LoginPage |
| `/register` | RegisterPage |
| `/dashboard` | DashboardPage — table + timeline tabs + Refresh + search |
| `/nifty50` | Nifty50Page — line chart + timeline tabs |
| `/stocks/:symbol` | StockPage — line chart + headlines |

Shared components: `<Toast />`, `<TimelineTabs />`, `<TrendBadge />`, `<ProtectedRoute />`.

Token stored in `localStorage`; axios interceptor injects `Authorization: Bearer <token>`.

## Project layout

```
gathari/
  backend/
    app/
      main.py
      db.py
      models.py
      schemas.py
      deps.py
      auth/        (routes.py, security.py)
      stocks/      (routes.py, fetcher.py, analyzer.py)
      nifty/       (routes.py, fetcher.py)
      news/        (routes.py, fetcher.py)
      refresh/     (routes.py)
      seed/        (nifty50.py, seed.py)
    alembic/
    requirements.txt
    .env.example
    Dockerfile
  frontend/
    src/
      pages/
      components/
      api/
      App.tsx
    package.json
    vite.config.ts
  docs/
```

## Deployment

| Service | Provider | Notes |
|---------|----------|-------|
| Frontend | Render Static Site (free) | Build: `npm run build`, publish dir: `dist`, env: `VITE_API_BASE_URL` |
| Backend | Render Web Service (free) | Build: `pip install -r requirements.txt`, start: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`; env: `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`. Sleeps after 15 min idle (cold start ~30s — acceptable for POC). |
| DB | Neon (free) | Same DB used for local dev and production. Auto-suspends; first query slow on cold start. |
| Migrations | Alembic | Run automatically on backend startup |
| Docker | Not used | Render native Python runtime; Neon replaces local Postgres |

## Out of scope (deferred)

- Configuration page
- Background scheduler / weekly jobs
- Password reset / email verification
- Admin UI
- Rate limiting
- Caching layer
- E2E tests (pytest only for analyzer + auth)
- NewsAPI fallback

## Build order

1. Backend skeleton + Postgres + Alembic + Nifty50 seed
2. Auth (register, login, JWT)
3. Stock fetcher + `/refresh` endpoint
4. Analyzer + `/dashboard`
5. Stock detail + Nifty50 endpoints
6. News fetcher
7. Frontend: login → dashboard → stock → nifty50
8. Deploy to Vercel + Render + Neon
9. Smoke test, hand off to small group
