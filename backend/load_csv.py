from __future__ import annotations

import argparse
import csv
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import psycopg2
import requests


INSERT_SQL = """
INSERT INTO popup_stores (
    name,
    address,
    start_date,
    end_date,
    source_url,
    source_domain,
    latitude,
    longitude,
    geom,
    popularity,
    dedupe_key
)
VALUES (
    %(name)s,
    %(address)s,
    %(start_date)s,
    %(end_date)s,
    %(source_url)s,
    %(source_domain)s,
    %(latitude)s,
    %(longitude)s,
    ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326),
    %(popularity)s,
    %(dedupe_key)s
)
ON CONFLICT (dedupe_key) DO NOTHING
"""

GEOCODE_FAILURE_HEADERS = [
    "name",
    "address",
    "start_date",
    "end_date",
    "source_url",
    "reason",
]


@dataclass(slots=True)
class CsvPopupRow:
    name: str
    address: str
    start_date: str
    end_date: str
    source_url: str
    source_domain: str


@dataclass(slots=True)
class GeocodedPopupRow(CsvPopupRow):
    latitude: float
    longitude: float
    dedupe_key: str
    popularity: int = 100


class KakaoLocalGeocoder:
    def __init__(self, api_key: str, timeout: int = 10) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"KakaoAK {self.api_key}"})

    def geocode(self, address: str) -> tuple[float, float] | None:
        response = self.session.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            params={"query": address},
            timeout=self.timeout,
        )
        response.raise_for_status()
        documents = response.json().get("documents", [])
        if not documents:
            return None
        first_hit = documents[0]
        latitude = float(first_hit["y"])
        longitude = float(first_hit["x"])
        return latitude, longitude


def default_database_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql:///popup_db")


def make_dedupe_key(row: CsvPopupRow) -> str:
    payload = "|".join(
        [
            row.name.strip().lower(),
            row.address.strip().lower(),
            row.start_date,
            row.end_date,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def read_csv_rows(csv_path: Path) -> list[CsvPopupRow]:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for raw in reader:
            rows.append(
                CsvPopupRow(
                    name=raw["name"],
                    address=raw["address"],
                    start_date=raw["start_date"],
                    end_date=raw["end_date"],
                    source_url=raw["source_url"],
                    source_domain=raw["source_domain"],
                )
            )
    return rows


def build_geocoded_row(
    row: CsvPopupRow,
    coordinates: tuple[float, float],
) -> GeocodedPopupRow:
    latitude, longitude = coordinates
    return GeocodedPopupRow(
        name=row.name,
        address=row.address,
        start_date=row.start_date,
        end_date=row.end_date,
        source_url=row.source_url,
        source_domain=row.source_domain,
        latitude=latitude,
        longitude=longitude,
        dedupe_key=make_dedupe_key(row),
    )


def insert_popup_row(cursor, row: GeocodedPopupRow) -> int:
    cursor.execute(
        INSERT_SQL,
        {
            "name": row.name,
            "address": row.address,
            "start_date": row.start_date,
            "end_date": row.end_date,
            "source_url": row.source_url,
            "source_domain": row.source_domain,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "popularity": row.popularity,
            "dedupe_key": row.dedupe_key,
        },
    )
    return cursor.rowcount


def write_failures(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GEOCODE_FAILURE_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def load_csv_to_db(
    csv_path: Path,
    database_url: str,
    kakao_api_key: str,
    failure_output: Path,
) -> tuple[int, int, int]:
    rows = read_csv_rows(csv_path)
    geocoder = KakaoLocalGeocoder(kakao_api_key)
    inserted = 0
    skipped = 0
    failures: list[dict[str, str]] = []

    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            for row in rows:
                try:
                    coordinates = geocoder.geocode(row.address)
                except requests.RequestException as exc:
                    failures.append(
                        {
                            "name": row.name,
                            "address": row.address,
                            "start_date": row.start_date,
                            "end_date": row.end_date,
                            "source_url": row.source_url,
                            "reason": f"kakao_error:{exc.__class__.__name__}",
                        }
                    )
                    continue

                if not coordinates:
                    failures.append(
                        {
                            "name": row.name,
                            "address": row.address,
                            "start_date": row.start_date,
                            "end_date": row.end_date,
                            "source_url": row.source_url,
                            "reason": "geocode_not_found",
                        }
                    )
                    continue

                result = insert_popup_row(cursor, build_geocoded_row(row, coordinates))
                if result:
                    inserted += 1
                else:
                    skipped += 1

    write_failures(failure_output, failures)
    return inserted, skipped, len(failures)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Load popup CSV into PostGIS.")
    parser.add_argument("--csv", default="data/interim/popup_stores.csv", type=Path)
    parser.add_argument(
        "--failure-output",
        default="data/interim/geocode_failures.csv",
        type=Path,
    )
    parser.add_argument("--database-url", default=default_database_url())
    parser.add_argument("--kakao-api-key", default=os.getenv("KAKAO_REST_API_KEY", ""))
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    if not args.kakao_api_key:
        raise SystemExit("KAKAO_REST_API_KEY is required to geocode addresses.")

    inserted, skipped, failures = load_csv_to_db(
        csv_path=args.csv,
        database_url=args.database_url,
        kakao_api_key=args.kakao_api_key,
        failure_output=args.failure_output,
    )
    print(f"Inserted rows: {inserted}")
    print(f"Skipped duplicates: {skipped}")
    print(f"Geocoding failures: {failures}")


if __name__ == "__main__":
    main()

