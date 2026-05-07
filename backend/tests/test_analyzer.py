from datetime import date, timedelta

import pytest

from app.stocks.analyzer import (
    STRONG_THRESHOLD,
    WEAK_THRESHOLD,
    aggregate_prices,
    compute_trend,
    timeline_cutoff,
)


# ---------------------------------------------------------------------------
# compute_trend
# ---------------------------------------------------------------------------

def _prices(n: int, start: float, step: float) -> list[float]:
    return [start + i * step for i in range(n)]


def test_compute_trend_strong_upward():
    closes = _prices(30, 100.0, 5.0)  # +5/day on mean ~172 → slope_pct >> 0.15
    result = compute_trend(closes)
    assert result["trend"] == "Strong Upward"
    assert result["slope_pct"] > STRONG_THRESHOLD


def test_compute_trend_strong_downward():
    closes = _prices(30, 500.0, -5.0)
    result = compute_trend(closes)
    assert result["trend"] == "Strong Downward"
    assert result["slope_pct"] < -STRONG_THRESHOLD


def test_compute_trend_neutral():
    # Flat line — slope is 0
    closes = [200.0] * 30
    result = compute_trend(closes)
    assert result["trend"] == "Neutral"
    assert result["slope_pct"] == 0.0


def test_compute_trend_weak_upward():
    # Tiny positive slope: +0.05 on mean 1000 → slope_pct = 0.005 %/day... need to engineer
    # Use slope that lands between WEAK and STRONG thresholds
    mean = 1000.0
    # slope_pct = slope/mean*100 → want 0.08 %/day → slope = 0.8 per day
    closes = [mean + i * 0.8 for i in range(30)]
    result = compute_trend(closes)
    assert result["trend"] == "Weak Upward"
    assert WEAK_THRESHOLD <= result["slope_pct"] < STRONG_THRESHOLD


def test_compute_trend_weak_downward():
    mean = 1000.0
    closes = [mean - i * 0.8 for i in range(30)]
    result = compute_trend(closes)
    assert result["trend"] == "Weak Downward"
    assert -STRONG_THRESHOLD < result["slope_pct"] <= -WEAK_THRESHOLD


def test_compute_trend_single_point_returns_neutral():
    result = compute_trend([150.0])
    assert result["trend"] == "Neutral"
    assert result["slope_pct"] == 0.0
    assert result["delta_pct"] == 0.0


def test_compute_trend_two_points():
    result = compute_trend([100.0, 200.0])
    assert result["trend"] in ("Strong Upward", "Weak Upward", "Neutral", "Weak Downward", "Strong Downward")


def test_compute_trend_delta_pct():
    closes = [100.0, 110.0, 120.0, 130.0, 150.0]
    result = compute_trend(closes)
    assert result["delta_pct"] == pytest.approx(50.0, abs=0.01)


# ---------------------------------------------------------------------------
# aggregate_prices
# ---------------------------------------------------------------------------

def _make_rows(n: int, start_date: date, step_days: int = 1) -> list[dict]:
    rows = []
    for i in range(n):
        d = start_date + timedelta(days=i * step_days)
        rows.append({
            "trade_date": d,
            "open": 100.0 + i,
            "high": 105.0 + i,
            "low": 95.0 + i,
            "close": 100.5 + i,
        })
    return rows


def test_aggregate_prices_1m_returns_daily():
    rows = _make_rows(20, date(2024, 1, 1))
    result = aggregate_prices(rows, "1M")
    assert result == rows  # no aggregation


def test_aggregate_prices_empty():
    assert aggregate_prices([], "2Y") == []


def test_aggregate_prices_2y_returns_monthly():
    # 365 daily rows → should collapse to ~12 months
    rows = _make_rows(365, date(2023, 1, 1))
    result = aggregate_prices(rows, "2Y")
    assert len(result) <= 12
    assert all("trade_date" in r and "close" in r for r in result)


def test_aggregate_prices_3m_returns_weekly():
    rows = _make_rows(90, date(2024, 1, 1))
    result = aggregate_prices(rows, "3M")
    # 90 days → ~13 weeks
    assert len(result) <= 13
    assert all("close" in r for r in result)


def test_aggregate_prices_output_types():
    rows = _make_rows(30, date(2024, 3, 1))
    result = aggregate_prices(rows, "6M")
    for r in result:
        assert isinstance(r["close"], float)
        assert isinstance(r["trade_date"], date)


# ---------------------------------------------------------------------------
# timeline_cutoff
# ---------------------------------------------------------------------------

def test_timeline_cutoff_1m():
    cutoff = timeline_cutoff("1M")
    assert cutoff == date.today() - timedelta(days=30)


def test_timeline_cutoff_2y():
    cutoff = timeline_cutoff("2Y")
    assert cutoff == date.today() - timedelta(days=730)


def test_timeline_cutoff_unknown_defaults_to_2y():
    cutoff = timeline_cutoff("INVALID")
    assert cutoff == date.today() - timedelta(days=730)
