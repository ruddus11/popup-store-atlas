from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel

from backend.app.config import get_settings
from backend.app.repository import DatabasePopupRepository, PopupRepository
from backend.app.security import (
    SlidingWindowRateLimiter,
    attach_rate_limit_headers,
    attach_security_headers,
    client_identifier,
    rate_limit_exceeded_response,
    should_apply_rate_limit,
)


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


settings = get_settings()
app = FastAPI(
    title="Popup Store API",
    version="1.0.0",
    docs_url="/docs" if settings.enable_api_docs else None,
    redoc_url="/redoc" if settings.enable_api_docs else None,
    openapi_url="/openapi.json" if settings.enable_api_docs else None,
)
rate_limiter = SlidingWindowRateLimiter(
    limit=settings.rate_limit_max_requests,
    window_seconds=settings.rate_limit_window_seconds,
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[host.strip() for host in settings.allowed_hosts.split(",") if host.strip()],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
)


def get_repository() -> PopupRepository:
    return DatabasePopupRepository(database_url=get_settings().database_url)


@app.middleware("http")
async def add_api_security(request: Request, call_next):
    is_api_request = should_apply_rate_limit(request)
    decision = None
    if is_api_request:
        decision = rate_limiter.check(client_identifier(request))
        if not decision.allowed:
            response = rate_limit_exceeded_response(decision)
            attach_security_headers(
                response,
                is_api_response=True,
                is_https=request.headers.get("x-forwarded-proto") == "https" or request.url.scheme == "https",
            )
            return response

    response = await call_next(request)
    if decision:
        attach_rate_limit_headers(response, decision)

    attach_security_headers(
        response,
        is_api_response=request.url.path.startswith("/api/") or request.url.path in {"/", "/health"},
        is_https=request.headers.get("x-forwarded-proto") == "https" or request.url.scheme == "https",
    )
    return response


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


@app.get("/api/popups/catalog", response_model=ActivePopupsResponse)
def read_popup_catalog(
    repository: Annotated[PopupRepository, Depends(get_repository)],
) -> ActivePopupsResponse:
    as_of_date, items = repository.fetch_catalog_popups()
    return ActivePopupsResponse(as_of_date=as_of_date, count=len(items), items=items)
