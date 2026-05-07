from datetime import date, timedelta

import pandas as pd
import yfinance as yf

_NIFTY_SYMBOL = "^NSEI"
_DEFAULT_LOOKBACK_DAYS = 365 * 2 + 10


def fetch_nifty50(since: date | None) -> list[dict]:
    """Download daily OHLC for Nifty50 index from since-date to today.

    since=None triggers a full 2-year backfill.
    Returns rows ready for upsert into nifty50_index.
    """
    from_date = since if since else date.today() - timedelta(days=_DEFAULT_LOOKBACK_DAYS)
    to_date = date.today() + timedelta(days=1)

    df: pd.DataFrame = yf.download(
        _NIFTY_SYMBOL,
        start=from_date.isoformat(),
        end=to_date.isoformat(),
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    if df.empty:
        return []

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"})
    df.index = pd.to_datetime(df.index).date  # type: ignore[assignment]

    rows = []
    for trade_date, row in df.iterrows():
        rows.append({
            "trade_date": trade_date,
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
        })
    return rows
