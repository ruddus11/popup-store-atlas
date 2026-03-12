from __future__ import annotations

from crawler.constants import ALLOWED_REGION_PREFIXES
from crawler.text_utils import normalize_text


def is_allowed_region(address: str) -> bool:
    normalized = normalize_text(address)
    return normalized.startswith(ALLOWED_REGION_PREFIXES)

