from __future__ import annotations

import re
from datetime import date

from bs4 import BeautifulSoup

from crawler.adapters.base import BaseAdapter
from crawler.address_hints import infer_address_from_text
from crawler.dates import SUPPORTED_DATE_RANGE_PATTERN
from crawler.models import RawPopupCandidate
from crawler.text_utils import clean_heading, normalize_text


class TistoryAdapter(BaseAdapter):
    domains = ("tistory.com",)

    _explicit_address_re = re.compile(
        r"(?:^|\s)주소[:\s]+(?P<address>(?:서울특별시|서울|경기도|경기|충청북도|충북|충청남도|충남|대전광역시|대전).*?)(?:기간[:\s]+|$)"
    )
    _fallback_address_re = re.compile(
        r"(?P<address>(?:서울특별시|서울|경기도|경기|충청북도|충북|충청남도|충남|대전광역시|대전)\s+[^\n,;)]*(?:로|길|대로)\s*\d+[^\n,;)]*)"
    )
    _period_re = re.compile(SUPPORTED_DATE_RANGE_PATTERN)

    def parse(self, html: str, source_url: str) -> list[RawPopupCandidate]:
        soup = BeautifulSoup(html, "html.parser")
        article = soup.select_one("#article-view, .entry-content") or soup
        published_date = self._extract_published_date(soup)
        parsed: list[RawPopupCandidate] = []

        for tag in article.find_all(["li", "p", "tr"]):
            text = normalize_text(tag.get_text(" ", strip=True))
            if not text:
                continue

            name = self._extract_name(tag, text)
            address = self._extract_address(text, name)
            period_match = self._period_re.search(text)
            raw_period = period_match.group(0) if period_match else ""

            if not any([name, address, raw_period]):
                continue

            candidate = RawPopupCandidate(
                name=name,
                address=address,
                raw_period=raw_period,
                source_url=source_url,
                source_domain=self.domains[0],
                published_date=published_date,
            )
            parsed.append(candidate)

        return self._dedupe_candidates(parsed)

    def _extract_published_date(self, soup: BeautifulSoup) -> date | None:
        meta = soup.find("meta", attrs={"property": "article:published_time"})
        if not meta or not meta.get("content"):
            return None
        return date.fromisoformat(meta["content"][:10])

    def _extract_name(self, tag, text: str) -> str:
        if tag.name == "tr":
            header_like = " ".join(cell.get_text(" ", strip=True) for cell in tag.find_all(["th", "td"]))
            return clean_heading(header_like)

        base_text = text
        emphasized = tag.find(["b", "strong"])
        if emphasized:
            base_text = normalize_text(emphasized.get_text(" ", strip=True))

        if "주소" in base_text:
            return clean_heading(base_text.split("주소", maxsplit=1)[0])

        period_match = self._period_re.search(base_text)
        if period_match:
            return clean_heading(base_text.split(period_match.group(0), maxsplit=1)[0])

        return clean_heading(base_text.split("(", maxsplit=1)[0])

    def _extract_address(self, text: str, name: str) -> str:
        explicit = self._explicit_address_re.search(text)
        if explicit:
            return normalize_text(explicit.group("address"))

        fallback = self._fallback_address_re.search(text)
        if fallback:
            return normalize_text(fallback.group("address"))

        return infer_address_from_text(f"{name} {text}")

    def _dedupe_candidates(self, candidates: list[RawPopupCandidate]) -> list[RawPopupCandidate]:
        deduped: list[RawPopupCandidate] = []
        for candidate in candidates:
            duplicate_index = next(
                (
                    index
                    for index, existing in enumerate(deduped)
                    if existing.address == candidate.address
                    and existing.raw_period == candidate.raw_period
                    and existing.source_url == candidate.source_url
                ),
                None,
            )
            if duplicate_index is None:
                deduped.append(candidate)
            continue

        return deduped
