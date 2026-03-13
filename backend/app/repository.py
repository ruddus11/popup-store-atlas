from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol

from psycopg2.extras import RealDictCursor

from backend.app.db import get_connection


ACTIVE_POPUPS_SQL = """
SELECT
    CURRENT_DATE AS as_of_date,
    id,
    name,
    address,
    start_date,
    end_date,
    latitude,
    longitude,
    source_url,
    popularity
FROM popup_stores
WHERE start_date <= CURRENT_DATE
  AND end_date >= CURRENT_DATE
  AND latitude IS NOT NULL
  AND longitude IS NOT NULL
ORDER BY end_date ASC, name ASC
"""

CATALOG_POPUPS_SQL = """
SELECT
    CURRENT_DATE AS as_of_date,
    id,
    name,
    address,
    start_date,
    end_date,
    latitude,
    longitude,
    source_url,
    popularity
FROM popup_stores
WHERE latitude IS NOT NULL
  AND longitude IS NOT NULL
ORDER BY start_date DESC, end_date DESC, name ASC
"""


class PopupRepository(Protocol):
    def fetch_active_popups(self) -> tuple[str, list[dict[str, Any]]]:
        ...

    def fetch_catalog_popups(self) -> tuple[str, list[dict[str, Any]]]:
        ...


@dataclass(slots=True)
class DatabasePopupRepository:
    database_url: str

    def fetch_active_popups(self) -> tuple[str, list[dict[str, Any]]]:
        return self._fetch_popups(ACTIVE_POPUPS_SQL)

    def fetch_catalog_popups(self) -> tuple[str, list[dict[str, Any]]]:
        return self._fetch_popups(CATALOG_POPUPS_SQL)

    def _fetch_popups(self, sql: str) -> tuple[str, list[dict[str, Any]]]:
        with get_connection(self.database_url) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                if not rows:
                    cursor.execute("SELECT CURRENT_DATE AS as_of_date")
                    as_of_date = cursor.fetchone()["as_of_date"]
                    return as_of_date.isoformat(), []

                as_of_value = rows[0]["as_of_date"]
                serialized = [serialize_popup_row(row) for row in rows]
                return as_of_value.isoformat(), serialized


def serialize_popup_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "address": row["address"],
        "start_date": _serialize_date(row["start_date"]),
        "end_date": _serialize_date(row["end_date"]),
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "source_url": row["source_url"],
        "popularity": int(row["popularity"]),
    }


def _serialize_date(value: date | str) -> str:
    return value.isoformat() if isinstance(value, date) else str(value)
