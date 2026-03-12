from fastapi.testclient import TestClient

from backend.app.main import app, get_repository


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
