import urllib.parse
from datetime import datetime, timezone

import feedparser

_RSS_BASE = "https://news.google.com/rss/search"
_MAX_ENTRIES = 15


def fetch_headlines(symbol: str, company_name: str) -> list[dict]:
    """Fetch up to 15 headlines from Google News RSS for a stock.

    Returns rows ready for upsert into headlines (ON CONFLICT DO NOTHING).
    """
    query = urllib.parse.quote(f"{company_name} NSE stock")
    url = f"{_RSS_BASE}?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

    feed = feedparser.parse(url)

    rows = []
    for entry in feed.entries[:_MAX_ENTRIES]:
        published_at: datetime | None = None
        if getattr(entry, "published_parsed", None):
            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

        source: str | None = None
        src = getattr(entry, "source", None)
        if src:
            source = getattr(src, "title", None)

        rows.append({
            "symbol": symbol,
            "headline": entry.get("title", ""),
            "url": entry.get("link", ""),
            "source": source,
            "published_at": published_at,
        })

    return [r for r in rows if r["url"]]  # drop any entries without a URL
