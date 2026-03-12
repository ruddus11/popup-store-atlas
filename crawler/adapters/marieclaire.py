from __future__ import annotations

import json
import re
from datetime import date

from bs4 import BeautifulSoup

from crawler.adapters.base import BaseAdapter
from crawler.dates import SUPPORTED_DATE_RANGE_PATTERN
from crawler.models import RawPopupCandidate
from crawler.text_utils import clean_heading, normalize_text


class MarieClaireAdapter(BaseAdapter):
    domains = ("marieclairekorea.com",)

    _address_period_re = re.compile(
        rf"주소\s*(?P<address>(?:서울|서울특별시|경기|경기도|충북|충청북도|충남|충청남도|대전|대전광역시).*?)"
        rf"기간\s*(?P<period>{SUPPORTED_DATE_RANGE_PATTERN})"
    )

    def parse(self, html: str, source_url: str) -> list[RawPopupCandidate]:
        soup = BeautifulSoup(html, "html.parser")
        published_date = self._extract_published_date(soup)
        heading_candidates = self._extract_headings(soup)
        article_body = self._extract_article_body(soup)

        if article_body:
            segments = list(self._address_period_re.finditer(article_body))
            if segments:
                return [
                    RawPopupCandidate(
                        name=heading_candidates[index] if index < len(heading_candidates) else f"popup-{index + 1}",
                        address=normalize_text(match.group("address")),
                        raw_period=normalize_text(match.group("period")),
                        source_url=source_url,
                        source_domain=self.domains[0],
                        published_date=published_date,
                    )
                    for index, match in enumerate(segments)
                ]

        return self._parse_dom_fallback(soup, source_url, published_date)

    def _extract_published_date(self, soup: BeautifulSoup) -> date | None:
        meta = soup.find("meta", attrs={"property": "article:published_time"})
        if not meta or not meta.get("content"):
            return None
        return date.fromisoformat(meta["content"][:10])

    def _extract_article_body(self, soup: BeautifulSoup) -> str:
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            if not script.string:
                continue
            try:
                payload = json.loads(script.string)
            except json.JSONDecodeError:
                continue
            article_body = payload.get("articleBody") if isinstance(payload, dict) else None
            if article_body:
                return normalize_text(article_body)
        return ""

    def _extract_headings(self, soup: BeautifulSoup) -> list[str]:
        headings: list[str] = []
        for tag in soup.find_all(["h2", "h3", "p"]):
            text = clean_heading(tag.get_text(" ", strip=True))
            if not text or "주소" in text or "기간" in text:
                continue
            if tag.name in {"h2", "h3"}:
                headings.append(text)
                continue
            strong_text = clean_heading(tag.get_text(" ", strip=True))
            if tag.find("strong") and len(strong_text) <= 90:
                headings.append(strong_text)
        return headings

    def _parse_dom_fallback(
        self,
        soup: BeautifulSoup,
        source_url: str,
        published_date: date | None,
    ) -> list[RawPopupCandidate]:
        current_name = ""
        parsed: list[RawPopupCandidate] = []

        for tag in soup.find_all(["h2", "h3", "p"]):
            text = normalize_text(tag.get_text(" ", strip=True))
            if not text:
                continue
            if "주소" in text and "기간" in text:
                address_match = re.search(r"주소\s*(.*?)\s*기간\s*(.*)$", text)
                if not address_match:
                    continue
                parsed.append(
                    RawPopupCandidate(
                        name=current_name or "unknown",
                        address=address_match.group(1),
                        raw_period=address_match.group(2),
                        source_url=source_url,
                        source_domain=self.domains[0],
                        published_date=published_date,
                    )
                )
                continue

            if tag.name in {"h2", "h3"} or (tag.find("strong") and len(text) <= 90):
                current_name = clean_heading(text)

        return parsed
