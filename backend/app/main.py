from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.config import settings
from app.nifty.routes import router as nifty_router
from app.refresh.routes import router as refresh_router
from app.stocks.routes import router as stocks_router

app = FastAPI(title="Gathari API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(refresh_router)
app.include_router(stocks_router)
app.include_router(nifty_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
