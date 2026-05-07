from datetime import date, datetime

from pydantic import BaseModel, field_validator


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    user_id: str
    user_name: str
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if info.data.get("password") and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    user_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    user_id: str
    user_name: str

    model_config = {"from_attributes": True}


# ── Shared ────────────────────────────────────────────────────────────────────

class PricePoint(BaseModel):
    trade_date: date
    open: float
    high: float
    low: float
    close: float

    model_config = {"from_attributes": True}


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardRow(BaseModel):
    symbol: str
    name: str
    industry: str | None
    trend: str
    slope_pct: float
    delta_pct: float
    last_price: float | None


class DashboardResponse(BaseModel):
    timeline: str
    rows: list[DashboardRow]


# ── Stock detail ──────────────────────────────────────────────────────────────

class HeadlineOut(BaseModel):
    headline: str
    url: str
    source: str | None
    published_at: datetime | None

    model_config = {"from_attributes": True}


class StockDetailResponse(BaseModel):
    symbol: str
    name: str
    industry: str | None
    timeline: str
    trend: str
    slope_pct: float
    delta_pct: float
    last_price: float | None
    prices: list[PricePoint]
    headlines: list[HeadlineOut]


# ── Nifty50 ───────────────────────────────────────────────────────────────────

class NiftyResponse(BaseModel):
    timeline: str
    prices: list[PricePoint]


# ── Refresh ───────────────────────────────────────────────────────────────────

class StockRefreshStatus(BaseModel):
    symbol: str
    status: str  # "ok" | "skipped" | "error"
    rows_added: int = 0
    detail: str | None = None
    news_status: str = "skipped"  # "ok" | "skipped" | "error"
    news_rows_added: int = 0


class NiftyRefreshStatus(BaseModel):
    status: str  # "ok" | "skipped" | "error"
    rows_added: int = 0
    detail: str | None = None


class RefreshResponse(BaseModel):
    stocks: list[StockRefreshStatus]
    nifty50: NiftyRefreshStatus
