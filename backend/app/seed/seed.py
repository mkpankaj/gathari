"""Idempotent seeder: inserts Nifty50 stocks if missing, fills industry from yfinance."""

from __future__ import annotations

import logging
import sys

import yfinance as yf
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Stock
from app.seed.nifty50 import COMPANY_NAMES, NIFTY_50

log = logging.getLogger(__name__)


def fetch_industry(symbol: str) -> str | None:
    try:
        info = yf.Ticker(symbol).info or {}
        return info.get("industry") or info.get("sector")
    except Exception as e:
        log.warning("industry lookup failed for %s: %s", symbol, e)
        return None


def run() -> None:
    with SessionLocal() as db:
        existing = {s.symbol for s in db.scalars(select(Stock)).all()}
        added = 0
        for symbol in NIFTY_50:
            if symbol in existing:
                continue
            stock = Stock(
                symbol=symbol,
                name=COMPANY_NAMES.get(symbol, symbol.replace(".NS", "")),
                industry=fetch_industry(symbol),
            )
            db.add(stock)
            added += 1
            print(f"  + {symbol} ({stock.industry or '—'})", flush=True)
        db.commit()
        print(f"Seed complete: {added} added, {len(existing)} already present.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        run()
    except Exception as e:
        print(f"Seed failed: {e}", file=sys.stderr)
        sys.exit(1)
