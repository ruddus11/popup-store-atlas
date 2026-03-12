from datetime import date

import pytest

from crawler.dates import parse_date_range
from crawler.filters import is_allowed_region


def test_parse_korean_date_range_with_inferred_year() -> None:
    start_date, end_date = parse_date_range(
        "2월 21일부터 3월 3일까지",
        reference_date=date(2025, 2, 18),
    )

    assert start_date.isoformat() == "2025-02-21"
    assert end_date.isoformat() == "2025-03-03"


def test_parse_numeric_date_range() -> None:
    start_date, end_date = parse_date_range("2025.08.01~2025.08.31")

    assert start_date.isoformat() == "2025-08-01"
    assert end_date.isoformat() == "2025-08-31"


def test_parse_invalid_date_range_raises() -> None:
    with pytest.raises(ValueError):
        parse_date_range("7월 말 ~ 9월 말")


def test_region_filter_allows_target_areas_only() -> None:
    assert is_allowed_region("서울 성동구 연무장길 114 1층") is True
    assert is_allowed_region("대전광역시 유성구 대학로 99") is True
    assert is_allowed_region("부산 해운대구 해운대로 264") is False

