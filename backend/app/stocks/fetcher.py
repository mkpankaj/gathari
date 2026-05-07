from datetime import date, timedelta

import pandas as pd
import yfinance as yf

_DEFAULT_LOOKBACK_DAYS = 365 * 2 + 10


def fetch_stock_prices(symbol: str, since: date | None) -> list[dict]:
    """Download daily OHLCV for symbol from since-date to today.

    since=None triggers a full 2-year backfill.
    Returns rows ready for upsert into stock_prices.
    """
    from_date = since if since else date.today() - timedelta(days=_DEFAULT_LOOKBACK_DAYS)
    to_date = date.today() + timedelta(days=1)  # yfinance end is exclusive

    df: pd.DataFrame = yf.download(
        symbol,
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

    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    df.index = pd.to_datetime(df.index).date  # type: ignore[assignment]

    rows = []
    for trade_date, row in df.iterrows():
        rows.append({
            "symbol": symbol,
            "trade_date": trade_date,
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": int(row["volume"]) if pd.notna(row.get("volume")) else None,
        })
    return rows
