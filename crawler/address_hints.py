from __future__ import annotations

import re

from crawler.text_utils import normalize_text

ADDRESS_HINTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"(더현대\s*서울|현대\s*서울|여의도\s*더현대|주토피아)", re.IGNORECASE),
        "서울 영등포구 여의대로 108 더현대 서울",
    ),
    (
        re.compile(r"(용산\s*아이파크몰|아이파크몰)", re.IGNORECASE),
        "서울 용산구 한강대로23길 55 아이파크몰",
    ),
    (
        re.compile(r"(성동구\s*연무장|연무장길?|연무장11길)", re.IGNORECASE),
        "서울 성동구 연무장길",
    ),
    (
        re.compile(r"(홍대|홍대입구)", re.IGNORECASE),
        "서울 마포구 양화로 188 홍대입구역",
    ),
    (
        re.compile(r"(성수동|성수역|성수)", re.IGNORECASE),
        "서울 성동구 성수동2가",
    ),
    (
        re.compile(r"(여의도\s*한강|서울\s*문|the\s*seoul\s*moon)", re.IGNORECASE),
        "서울 영등포구 여의동로 330 여의도한강공원",
    ),
    (
        re.compile(r"(용산)", re.IGNORECASE),
        "서울 용산구 한강대로23길 55 아이파크몰",
    ),
)


def infer_address_from_text(text: str) -> str:
    normalized = normalize_text(text)
    if not normalized:
        return ""

    for pattern, address in ADDRESS_HINTS:
        if pattern.search(normalized):
            return address
    return ""
