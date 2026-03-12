from __future__ import annotations

import os
from functools import lru_cache


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "postgresql:///popup_db")
        self.cors_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        self.allowed_hosts = os.getenv(
            "ALLOWED_HOSTS",
            "localhost,127.0.0.1,testserver,popup-store-api.onrender.com",
        )
        self.rate_limit_window_seconds = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
        self.rate_limit_max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))
        self.enable_api_docs = os.getenv("ENABLE_API_DOCS", "").lower() in {"1", "true", "yes"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
