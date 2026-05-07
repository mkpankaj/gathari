from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Headline, Stock, StockPrice, User
from app.schemas import DashboardResponse, DashboardRow, StockDetailResponse
from app.stocks.analyzer import aggregate_prices, compute_trend, timeline_cutoff

router = APIRouter(prefix="/api", tags=["stocks"])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    timeline: str = Query(default="2Y", pattern="^(1M|3M|6M|9M|1Y|1\\.5Y|2Y)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    cutoff = timeline_cutoff(timeline)

    stocks = {s.symbol: s for s in db.scalars(select(Stock)).all()}

    prices_q = (
        select(StockPrice)
        .where(StockPrice.trade_date >= cutoff)
        .order_by(StockPrice.symbol, StockPrice.trade_date)
    )
    by_symbol: dict[str, list[float]] = defaultdict(list)
    last_price: dict[str, float] = {}
    for sp in db.scalars(prices_q):
        by_symbol[sp.symbol].append(float(sp.close))
        last_price[sp.symbol] = float(sp.close)

    rows: list[DashboardRow] = []
    for symbol, stock in stocks.items():
        closes = by_symbol.get(symbol, [])
        if closes:
            metrics = compute_trend(closes)
        else:
            metrics = {"trend": "Neutral", "slope_pct": 0.0, "delta_pct": 0.0}

        rows.append(DashboardRow(
            symbol=symbol,
            name=stock.name,
            industry=stock.industry,
            trend=metrics["trend"],
            slope_pct=metrics["slope_pct"],
            delta_pct=metrics["delta_pct"],
            last_price=last_price.get(symbol),
        ))

    rows.sort(key=lambda r: r.symbol)
    return DashboardResponse(timeline=timeline, rows=rows)


@router.get("/stocks/{symbol}", response_model=StockDetailResponse)
def stock_detail(
    symbol: str,
    timeline: str = Query(default="2Y", pattern="^(1M|3M|6M|9M|1Y|1\\.5Y|2Y)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stock = db.scalar(select(Stock).where(Stock.symbol == symbol))
    if not stock:
        raise HTTPException(status_code=404, detail="Symbol not found")

    cutoff = timeline_cutoff(timeline)

    price_rows = [
        {"trade_date": sp.trade_date, "open": float(sp.open), "high": float(sp.high),
         "low": float(sp.low), "close": float(sp.close)}
        for sp in db.scalars(
            select(StockPrice)
            .where(StockPrice.symbol == symbol, StockPrice.trade_date >= cutoff)
            .order_by(StockPrice.trade_date)
        )
    ]

    closes = [r["close"] for r in price_rows]
    metrics = compute_trend(closes) if closes else {"trend": "Neutral", "slope_pct": 0.0, "delta_pct": 0.0}

    headlines = db.scalars(
        select(Headline)
        .where(Headline.symbol == symbol)
        .order_by(Headline.published_at.desc().nullslast())
        .limit(20)
    ).all()

    return StockDetailResponse(
        symbol=stock.symbol,
        name=stock.name,
        industry=stock.industry,
        timeline=timeline,
        trend=metrics["trend"],
        slope_pct=metrics["slope_pct"],
        delta_pct=metrics["delta_pct"],
        last_price=closes[-1] if closes else None,
        prices=aggregate_prices(price_rows, timeline),
        headlines=headlines,
    )
