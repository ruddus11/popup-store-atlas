from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date


@dataclass(slots=True)
class RawPopupCandidate:
    name: str
    address: str
    raw_period: str
    source_url: str
    source_domain: str
    published_date: date | None = None


@dataclass(slots=True)
class PopupRow:
    name: str
    address: str
    start_date: str
    end_date: str
    source_url: str
    source_domain: str
    collected_at: str

    def to_csv_row(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class RejectedRow:
    reason: str
    name: str
    address: str
    raw_period: str
    source_url: str
    source_domain: str

    def to_csv_row(self) -> dict[str, str]:
        return asdict(self)

