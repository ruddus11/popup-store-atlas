from backend.load_csv import (
    CsvPopupRow,
    build_geocoded_row,
    insert_popup_row,
    make_dedupe_key,
)
from crawler.url_utils import validate_source_url


class FakeCursor:
    def __init__(self, rowcount: int = 1) -> None:
        self.rowcount = rowcount
        self.executed: list[tuple[str, dict[str, object]]] = []

    def execute(self, sql: str, params: dict[str, object]) -> None:
        self.executed.append((sql, params))


def test_make_dedupe_key_is_stable() -> None:
    row = CsvPopupRow(
        name="AHC",
        address="서울 성동구 연무장11길 13",
        start_date="2025-02-21",
        end_date="2025-03-03",
        source_url="https://example.com/ahc",
        source_domain="example.com",
    )

    assert make_dedupe_key(row) == make_dedupe_key(row)


def test_insert_popup_row_uses_postgis_point_insert() -> None:
    cursor = FakeCursor()
    row = CsvPopupRow(
        name="AHC",
        address="서울 성동구 연무장11길 13",
        start_date="2025-02-21",
        end_date="2025-03-03",
        source_url="https://example.com/ahc",
        source_domain="example.com",
    )
    geocoded = build_geocoded_row(row, (37.5432, 127.0568))

    inserted = insert_popup_row(cursor, geocoded)

    assert inserted == 1
    assert "ST_SetSRID(ST_MakePoint" in cursor.executed[0][0]
    assert cursor.executed[0][1]["longitude"] == 127.0568
    assert cursor.executed[0][1]["latitude"] == 37.5432


def test_validate_source_url_allows_subdomains_only_on_dot_boundary() -> None:
    normalized, error = validate_source_url(
        "https://www.marieclairekorea.com/newnew/2025/02/march-pop-up/",
        allowed_domains=("marieclairekorea.com",),
    )

    assert error is None
    assert normalized == "https://www.marieclairekorea.com/newnew/2025/02/march-pop-up/"

    normalized, error = validate_source_url(
        "https://evilmarieclairekorea.com/newnew/2025/02/march-pop-up/",
        allowed_domains=("marieclairekorea.com",),
    )

    assert normalized is None
    assert error == "unsupported_source_domain"
