from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock

from fastapi import Request
from starlette.responses import JSONResponse, Response


@dataclass(slots=True)
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, now: float | None = None) -> RateLimitDecision:
        timestamp = now or time.time()
        with self._lock:
            hits = self._hits[key]
            window_start = timestamp - self.window_seconds
            while hits and hits[0] <= window_start:
                hits.popleft()

            if len(hits) >= self.limit:
                retry_after = max(1, int(hits[0] + self.window_seconds - timestamp))
                return RateLimitDecision(
                    allowed=False,
                    limit=self.limit,
                    remaining=0,
                    retry_after=retry_after,
                )

            hits.append(timestamp)
            remaining = max(0, self.limit - len(hits))
            return RateLimitDecision(
                allowed=True,
                limit=self.limit,
                remaining=remaining,
                retry_after=0,
            )


def client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
        if client_ip:
            return client_ip

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def should_apply_rate_limit(request: Request) -> bool:
    return request.method == "GET" and request.url.path.startswith("/api/")


def attach_rate_limit_headers(response: Response, decision: RateLimitDecision) -> None:
    response.headers["X-RateLimit-Limit"] = str(decision.limit)
    response.headers["X-RateLimit-Remaining"] = str(decision.remaining)
    if decision.retry_after:
        response.headers["Retry-After"] = str(decision.retry_after)


def rate_limit_exceeded_response(decision: RateLimitDecision) -> JSONResponse:
    response = JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please retry later."},
    )
    attach_rate_limit_headers(response, decision)
    return response


def attach_security_headers(response: Response, *, is_api_response: bool, is_https: bool) -> None:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-site"

    if is_https:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

    if is_api_response:
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
        )
