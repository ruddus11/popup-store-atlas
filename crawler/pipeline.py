from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from crawler.dates import parse_date_range
from crawler.filters import is_allowed_region
from crawler.models import PopupRow, RawPopupCandidate, RejectedRow
from crawler.text_utils import normalize_text

SEOUL_TZ = ZoneInfo("Asia/Seoul")


def normalize_candidate(
    candidate: RawPopupCandidate,
    collected_at: datetime | None = None,
) -> tuple[PopupRow | None, RejectedRow | None]:
    name = normalize_text(candidate.name)
    address = normalize_text(candidate.address)
    raw_period = normalize_text(candidate.raw_period)

    if not name:
        return None, RejectedRow(
            reason="missing_name",
            name=name,
            address=address,
            raw_period=raw_period,
            source_url=candidate.source_url,
            source_domain=candidate.source_domain,
        )

    if not address:
        return None, RejectedRow(
            reason="missing_address",
            name=name,
            address=address,
            raw_period=raw_period,
            source_url=candidate.source_url,
            source_domain=candidate.source_domain,
        )

    if not raw_period:
        return None, RejectedRow(
            reason="missing_period",
            name=name,
            address=address,
            raw_period=raw_period,
            source_url=candidate.source_url,
            source_domain=candidate.source_domain,
        )

    if not is_allowed_region(address):
        return None, RejectedRow(
            reason="unsupported_region",
            name=name,
            address=address,
            raw_period=raw_period,
            source_url=candidate.source_url,
            source_domain=candidate.source_domain,
        )

    try:
        start_date, end_date = parse_date_range(raw_period, candidate.published_date)
    except ValueError:
        return None, RejectedRow(
            reason="invalid_period",
            name=name,
            address=address,
            raw_period=raw_period,
            source_url=candidate.source_url,
            source_domain=candidate.source_domain,
        )

    timestamp = (collected_at or datetime.now(SEOUL_TZ)).isoformat(timespec="seconds")
    return (
        PopupRow(
            name=name,
            address=address,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            source_url=candidate.source_url,
            source_domain=candidate.source_domain,
            collected_at=timestamp,
        ),
        None,
    )

