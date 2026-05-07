from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str

    @field_validator("database_url", mode="before")
    @classmethod
    def _fix_db_scheme(cls, v: str) -> str:
        # Neon and most providers give postgresql:// or postgres://, which SQLAlchemy
        # routes to psycopg2. Force psycopg (v3) so requirements.txt stays consistent.
        for prefix in ("postgresql://", "postgres://"):
            if v.startswith(prefix):
                return "postgresql+psycopg" + v[len(prefix) - 3:]
        return v
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
