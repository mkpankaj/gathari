from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Nifty50Index, User
from app.schemas import NiftyResponse
from app.stocks.analyzer import aggregate_prices, timeline_cutoff

router = APIRouter(prefix="/api", tags=["nifty50"])


@router.get("/nifty50", response_model=NiftyResponse)
def nifty50(
    timeline: str = Query(default="2Y", pattern="^(1M|3M|6M|9M|1Y|1\\.5Y|2Y)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    cutoff = timeline_cutoff(timeline)

    price_rows = [
        {"trade_date": row.trade_date, "open": float(row.open), "high": float(row.high),
         "low": float(row.low), "close": float(row.close)}
        for row in db.scalars(
            select(Nifty50Index)
            .where(Nifty50Index.trade_date >= cutoff)
            .order_by(Nifty50Index.trade_date)
        )
    ]

    return NiftyResponse(timeline=timeline, prices=aggregate_prices(price_rows, timeline))
