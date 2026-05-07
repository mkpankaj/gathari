from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


def _coerce_url(url: str) -> str:
    # Neon (and most providers) give postgresql:// or postgres:// which SQLAlchemy
    # maps to the psycopg2 dialect. We use psycopg (v3), so force the right driver.
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg" + url[len(prefix) - 3:]
    return url


engine = create_engine(_coerce_url(settings.database_url), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass
