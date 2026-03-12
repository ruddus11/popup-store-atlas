from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.config import get_settings
from backend.app.repository import DatabasePopupRepository, PopupRepository


class PopupItem(BaseModel):
    id: int
    name: str
    address: str
    start_date: str
    end_date: str
    latitude: float
    longitude: float
    source_url: str
    popularity: int


class ActivePopupsResponse(BaseModel):
    as_of_date: str
    count: int
    items: list[PopupItem]


class HealthResponse(BaseModel):
    status: str


app = FastAPI(title="Popup Store API", version="1.0.0")
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_repository() -> PopupRepository:
    return DatabasePopupRepository(database_url=get_settings().database_url)


@app.get("/", response_model=HealthResponse)
def read_root() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/popups/active", response_model=ActivePopupsResponse)
def read_active_popups(
    repository: Annotated[PopupRepository, Depends(get_repository)],
) -> ActivePopupsResponse:
    as_of_date, items = repository.fetch_active_popups()
    return ActivePopupsResponse(as_of_date=as_of_date, count=len(items), items=items)

