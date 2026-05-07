from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Headline, Nifty50Index, Nifty50Meta, Stock, StockPrice, User
from app.news.fetcher import fetch_headlines
from app.nifty.fetcher import fetch_nifty50
from app.schemas import NiftyRefreshStatus, RefreshResponse, StockRefreshStatus
from app.stocks.fetcher import fetch_stock_prices

router = APIRouter(prefix="/api/refresh", tags=["refresh"])

_NEWS_STALE_DAYS = 30


def _news_is_stale(last_fetch: date | None) -> bool:
    if last_fetch is None:
        return True
    return (date.today() - last_fetch).days > _NEWS_STALE_DAYS


@router.post("", response_model=RefreshResponse)
def refresh(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    today = date.today()
    stock_statuses: list[StockRefreshStatus] = []

    for stock in db.scalars(select(Stock)).all():
        price_status = "skipped"
        rows_added = 0
        detail = None
        news_status = "skipped"
        news_rows_added = 0

        # ── prices ──────────────────────────────────────────────────────────
        if stock.last_fetch_date != today:
            try:
                rows = fetch_stock_prices(stock.symbol, stock.last_fetch_date)
                if rows:
                    stmt = pg_insert(StockPrice).values(rows)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["symbol", "trade_date"],
                        set_={c: stmt.excluded[c] for c in ("open", "high", "low", "close", "volume")},
                    )
                    db.execute(stmt)
                stock.last_fetch_date = today
                db.commit()
                price_status = "ok"
                rows_added = len(rows)
            except Exception as exc:
                db.rollback()
                price_status = "error"
                detail = str(exc)

        # ── news (non-fatal; skip if prices errored to avoid partial state) ─
        if price_status != "error" and _news_is_stale(stock.last_fetch_date_news):
            try:
                headlines = fetch_headlines(stock.symbol, stock.name)
                if headlines:
                    stmt = pg_insert(Headline).values(headlines)
                    stmt = stmt.on_conflict_do_nothing(
                        index_elements=["symbol", "url"],
                    )
                    result = db.execute(stmt)
                    news_rows_added = result.rowcount if result.rowcount >= 0 else len(headlines)
                stock.last_fetch_date_news = today
                db.commit()
                news_status = "ok"
            except Exception:
                db.rollback()
                news_status = "error"

        stock_statuses.append(StockRefreshStatus(
            symbol=stock.symbol,
            status=price_status,
            rows_added=rows_added,
            detail=detail,
            news_status=news_status,
            news_rows_added=news_rows_added,
        ))

    # ── Nifty50 index ────────────────────────────────────────────────────────
    meta = db.scalar(select(Nifty50Meta))
    if meta is None:
        meta = Nifty50Meta(id=1)
        db.add(meta)
        db.flush()

    if meta.last_fetch_date == today:
        nifty_status = NiftyRefreshStatus(status="skipped")
    else:
        try:
            rows = fetch_nifty50(meta.last_fetch_date)
            if rows:
                stmt = pg_insert(Nifty50Index).values(rows)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["trade_date"],
                    set_={c: stmt.excluded[c] for c in ("open", "high", "low", "close")},
                )
                db.execute(stmt)
            meta.last_fetch_date = today
            db.commit()
            nifty_status = NiftyRefreshStatus(status="ok", rows_added=len(rows))
        except Exception as exc:
            db.rollback()
            nifty_status = NiftyRefreshStatus(status="error", detail=str(exc))

    return RefreshResponse(stocks=stock_statuses, nifty50=nifty_status)
