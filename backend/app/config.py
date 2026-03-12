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


@lru_cache
def get_settings() -> Settings:
    return Settings()

