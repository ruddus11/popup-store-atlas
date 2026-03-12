from __future__ import annotations

import re
from datetime import date

from crawler.text_utils import normalize_text

KOREAN_DATE_RANGE_PATTERN = (
    r"(?:(?P<sy>\d{4})년\s*)?"
    r"(?P<sm>\d{1,2})월\s*(?P<sd>\d{1,2})일?\s*"
    r"(?:부터|~|-|–)\s*"
    r"(?:(?P<ey>\d{4})년\s*)?"
    r"(?P<em>\d{1,2})월\s*(?P<ed>\d{1,2})일?\s*"
    r"(?:까지)?"
)

NUMERIC_DATE_RANGE_PATTERN = (
    r"(?:(?P<nsy>\d{4})[./-])?"
    r"(?P<nsm>\d{1,2})[./-](?P<nsd>\d{1,2})\s*"
    r"(?:~|-|–)\s*"
    r"(?:(?P<ney>\d{4})[./-])?"
    r"(?P<nem>\d{1,2})[./-](?P<ned>\d{1,2})"
)

SUPPORTED_DATE_RANGE_PATTERN = rf"(?:{KOREAN_DATE_RANGE_PATTERN}|{NUMERIC_DATE_RANGE_PATTERN})"

KOREAN_DATE_RANGE_RE = re.compile(KOREAN_DATE_RANGE_PATTERN)
NUMERIC_DATE_RANGE_RE = re.compile(NUMERIC_DATE_RANGE_PATTERN)


def _infer_year(
    explicit_year: str | None,
    fallback_year: int,
) -> int:
    return int(explicit_year) if explicit_year else fallback_year


def parse_date_range(raw_period: str, reference_date: date | None = None) -> tuple[date, date]:
    normalized = normalize_text(raw_period)
    reference = reference_date or date.today()

    korean_match = KOREAN_DATE_RANGE_RE.search(normalized)
    if korean_match:
        start_year = _infer_year(korean_match.group("sy"), reference.year)
        start_month = int(korean_match.group("sm"))
        start_day = int(korean_match.group("sd"))
        end_year = _infer_year(korean_match.group("ey"), start_year)
        end_month = int(korean_match.group("em"))
        end_day = int(korean_match.group("ed"))
        if not korean_match.group("ey") and (end_month, end_day) < (start_month, start_day):
            end_year += 1
        return date(start_year, start_month, start_day), date(end_year, end_month, end_day)

    numeric_match = NUMERIC_DATE_RANGE_RE.search(normalized)
    if numeric_match:
        start_year = _infer_year(numeric_match.group("nsy"), reference.year)
        start_month = int(numeric_match.group("nsm"))
        start_day = int(numeric_match.group("nsd"))
        end_year = _infer_year(numeric_match.group("ney"), start_year)
        end_month = int(numeric_match.group("nem"))
        end_day = int(numeric_match.group("ned"))
        if not numeric_match.group("ney") and (end_month, end_day) < (start_month, start_day):
            end_year += 1
        return date(start_year, start_month, start_day), date(end_year, end_month, end_day)

    raise ValueError(f"Unsupported date range: {raw_period}")

