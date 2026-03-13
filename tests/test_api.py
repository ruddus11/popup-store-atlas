from fastapi.testclient import TestClient

from backend.app.main import app, get_repository, rate_limiter


class FakeRepository:
    def fetch_active_popups(self):
        return (
            "2026-03-12",
            [
                {
                    "id": 1,
                    "name": "AHC SKIN GAME T SHOT 팝업",
                    "address": "서울 성동구 연무장11길 13",
                    "start_date": "2026-03-01",
                    "end_date": "2026-03-31",
                    "latitude": 37.5432,
                    "longitude": 127.0568,
                    "source_url": "https://example.com/ahc",
                    "popularity": 100,
                }
            ],
        )

    def fetch_catalog_popups(self):
        return (
            "2026-03-12",
            [
                {
                    "id": 2,
                    "name": "종료된 팝업",
                    "address": "서울 용산구 한강대로23길 55",
                    "start_date": "2025-02-21",
                    "end_date": "2025-03-06",
                    "latitude": 37.529,
                    "longitude": 126.965,
                    "source_url": "https://example.com/ended",
                    "popularity": 100,
                }
            ],
        )


def test_active_popups_endpoint_returns_coordinates_as_numbers() -> None:
    app.dependency_overrides[get_repository] = lambda: FakeRepository()
    client = TestClient(app)

    response = client.get("/api/popups/active")

    app.dependency_overrides.clear()
    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 1
    assert isinstance(payload["items"][0]["latitude"], float)
    assert isinstance(payload["items"][0]["longitude"], float)
    assert payload["items"][0]["name"] == "AHC SKIN GAME T SHOT 팝업"


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_catalog_endpoint_returns_all_popups() -> None:
    app.dependency_overrides[get_repository] = lambda: FakeRepository()
    client = TestClient(app)

    response = client.get("/api/popups/catalog")

    app.dependency_overrides.clear()
    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["items"][0]["name"] == "종료된 팝업"


def test_cors_disables_credentials_for_public_api() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/popups/active",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-credentials" not in response.headers


def test_api_responses_include_security_headers() -> None:
    app.dependency_overrides[get_repository] = lambda: FakeRepository()
    client = TestClient(app)

    response = client.get("/api/popups/active")

    app.dependency_overrides.clear()
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["content-security-policy"].startswith("default-src 'none'")


def test_docs_are_disabled_by_default() -> None:
    client = TestClient(app)

    response = client.get("/docs")

    assert response.status_code == 404


def test_untrusted_host_is_rejected() -> None:
    client = TestClient(app)

    response = client.get("/health", headers={"host": "evil.example.com"})

    assert response.status_code == 400


def test_api_rate_limit_returns_429_after_limit() -> None:
    app.dependency_overrides[get_repository] = lambda: FakeRepository()
    client = TestClient(app)
    original_limit = rate_limiter.limit
    original_window = rate_limiter.window_seconds
    rate_limiter.limit = 2
    rate_limiter.window_seconds = 60
    rate_limiter._hits.clear()

    try:
        assert client.get("/api/popups/active").status_code == 200
        assert client.get("/api/popups/active").status_code == 200
        third = client.get("/api/popups/active")
    finally:
        app.dependency_overrides.clear()
        rate_limiter.limit = original_limit
        rate_limiter.window_seconds = original_window
        rate_limiter._hits.clear()

    assert third.status_code == 429
    assert third.headers["x-ratelimit-limit"] == "2"
    assert third.headers["x-ratelimit-remaining"] == "0"
