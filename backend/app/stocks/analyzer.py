from datetime import date, timedelta
from typing import Literal

import numpy as np
import pandas as pd

# %/day slope thresholds for trend classification
STRONG_THRESHOLD = 0.15
WEAK_THRESHOLD = 0.05

TrendLabel = Literal["Strong Upward", "Weak Upward", "Neutral", "Weak Downward", "Strong Downward"]

TIMELINE_DAYS: dict[str, int] = {
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "9M": 270,
    "1Y": 365,
    "1.5Y": 548,
    "2Y": 730,
}


def timeline_cutoff(timeline: str) -> date:
    days = TIMELINE_DAYS.get(timeline, TIMELINE_DAYS["2Y"])
    return date.today() - timedelta(days=days)


def compute_trend(closes: list[float]) -> dict:
    """Linear regression on close prices; returns trend label and key metrics."""
    if len(closes) < 2:
        return {"trend": "Neutral", "slope_pct": 0.0, "delta_pct": 0.0}

    xs = np.arange(len(closes), dtype=float)
    ys = np.array(closes, dtype=float)

    slope, _ = np.polyfit(xs, ys, 1)
    mean_close = float(np.mean(ys))
    slope_pct = (slope / mean_close * 100) if mean_close else 0.0
    delta_pct = ((closes[-1] - closes[0]) / closes[0] * 100) if closes[0] else 0.0

    if slope_pct >= STRONG_THRESHOLD:
        label: TrendLabel = "Strong Upward"
    elif slope_pct >= WEAK_THRESHOLD:
        label = "Weak Upward"
    elif slope_pct <= -STRONG_THRESHOLD:
        label = "Strong Downward"
    elif slope_pct <= -WEAK_THRESHOLD:
        label = "Weak Downward"
    else:
        label = "Neutral"

    return {"trend": label, "slope_pct": round(slope_pct, 4), "delta_pct": round(delta_pct, 2)}


# 1M → daily | 3M, 6M → weekly | 9M+ → monthly
_RESAMPLE_FREQ: dict[str, str | None] = {
    "1M": None,
    "3M": "W",
    "6M": "W",
    "9M": "MS",
    "1Y": "MS",
    "1.5Y": "MS",
    "2Y": "MS",
}


def aggregate_prices(rows: list[dict], timeline: str) -> list[dict]:
    """Aggregate OHLC rows per the timeline bucket rules.

    rows must contain keys: trade_date, open, high, low, close (floats).
    Returns same structure with aggregated (mean) values.
    """
    if not rows:
        return []

    freq = _RESAMPLE_FREQ.get(timeline)
    if freq is None:
        return rows  # 1M → daily, no aggregation

    df = pd.DataFrame(rows)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df.sort_values("trade_date").set_index("trade_date")

    agg = df[["open", "high", "low", "close"]].resample(freq).mean().dropna()

    result = []
    for dt, row in agg.iterrows():
        result.append({
            "trade_date": dt.date(),
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
        })
    return result
