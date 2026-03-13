from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlsplit

from crawler.adapters.base import BaseAdapter
from crawler.http import build_session
from crawler.models import RawPopupCandidate
from crawler.text_utils import clean_heading, normalize_text


@dataclass(frozen=True, slots=True)
class BranchInfo:
    name: str
    address: str


class EhyundaiAdapter(BaseAdapter):
    domains = ("ehyundai.com",)

    _mbl_dm_cd_re = re.compile(r"var\s+curtMblDmCd\s*=\s*'([^']+)'")
    _popup_re = re.compile(r"(pop[\s-]?up|팝업)", re.IGNORECASE)
    _prefix_re = re.compile(r"^\[(?:POP[\s-]?UP(?:\s+STORE)?)\]\s*", re.IGNORECASE)
    _ignored_location_tokens = {"", "미입력", "직접입력", "직접 입력"}

    _branches: dict[str, BranchInfo] = {
        "B00126000": BranchInfo("천호점", "서울특별시 강동구 천호대로 1005"),
        "B00142000": BranchInfo("목동점", "서울특별시 양천구 목동동로 257"),
        "B00143000": BranchInfo("중동점", "경기 부천시 길주로 180 원미구 (중동, 현대백화점중동점)"),
        "B00145000": BranchInfo("킨텍스점", "경기도 고양시 일산서구 호수로 817"),
        "B00147000": BranchInfo("충청점", "충북 청주시 흥덕구 직지대로 308"),
        "B00148000": BranchInfo("판교점", "경기도 성남시 분당구 판교역로146번길 20"),
        "B00177000": BranchInfo("대전점", "대전광역시 유성구 테크노중앙로 123"),
        "B00179000": BranchInfo("커넥트현대 청주", "충북 청주시 흥덕구 가경동 1416"),
        "B00140000": BranchInfo("더현대 서울", "서울 영등포구 여의대로 108 (여의도동, 파크원)"),
    }

    def parse(self, html: str, source_url: str) -> list[RawPopupCandidate]:
        branch_code = self._extract_branch_code(source_url)
        if not branch_code or branch_code not in self._branches:
            return []

        mbl_dm_cd = self._extract_mbl_dm_cd(html)
        if not mbl_dm_cd:
            return []

        seen_codes: set[str] = set()
        candidates: list[RawPopupCandidate] = []

        for item in self._fetch_listing_items(mbl_dm_cd):
            event_code = normalize_text(str(item.get("evntCrdCd") or ""))
            if not event_code or event_code in seen_codes:
                continue

            candidate = self._candidate_from_item(item, branch_code)
            if candidate is None:
                continue

            seen_codes.add(event_code)
            candidates.append(candidate)

        return candidates

    def _extract_branch_code(self, source_url: str) -> str:
        parsed = urlsplit(source_url)
        return parse_qs(parsed.query).get("branchCd", [""])[0]

    def _extract_mbl_dm_cd(self, html: str) -> str:
        match = self._mbl_dm_cd_re.search(html)
        return match.group(1) if match else ""

    def _fetch_listing_items(self, mbl_dm_cd: str) -> list[dict[str, Any]]:
        session = build_session()
        session.headers["X-Requested-With"] = "XMLHttpRequest"
        page_size = 100
        page = 1
        total_pages = 1
        items: list[dict[str, Any]] = []

        while page <= total_pages:
            response = session.get(
                "https://www.ehyundai.com/newPortal/SN/GetCmsContentsAJX.do",
                params={
                    "apiID": "ifAppHdcms012",
                    "param": f"mblDmCd={mbl_dm_cd}&evntCrdTypeCd=01&pageSize={page_size}&page={page}",
                },
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json().get("result", {})
            page_items = payload.get("items", [])
            if not isinstance(page_items, list):
                break

            items.extend(page_items)
            total_count = int(payload.get("totalCount", len(page_items)) or 0)
            total_pages = max(1, math.ceil(total_count / page_size))
            page += 1

        return items

    def _candidate_from_item(self, item: dict[str, Any], branch_code: str) -> RawPopupCandidate | None:
        raw_name = normalize_text(str(item.get("evntCrdNm") or ""))
        name = self._normalize_event_name(raw_name)
        place = normalize_text(str(item.get("evntPlceNm") or ""))
        floor = normalize_text(self._extract_label(item.get("evntFlrCd")))
        if not self._is_popup_item(raw_name, place):
            return None

        raw_period = self._build_period(item)
        address = self._build_address(branch_code, floor, place)
        event_code = normalize_text(str(item.get("evntCrdCd") or ""))
        if not event_code:
            return None

        return RawPopupCandidate(
            name=name,
            address=address,
            raw_period=raw_period,
            source_url=self._build_detail_url(branch_code, event_code),
            source_domain=self.domains[0],
        )

    def _normalize_event_name(self, value: str) -> str:
        normalized = normalize_text(value)
        normalized = self._prefix_re.sub("", normalized)
        return clean_heading(normalized)

    def _is_popup_item(self, name: str, place: str) -> bool:
        haystack = f"{name} {place}"
        return bool(self._popup_re.search(haystack))

    def _build_period(self, item: dict[str, Any]) -> str:
        start = self._extract_date(item.get("expsEvntStartDt")) or self._extract_date(item.get("evntStrtDt"))
        end = self._extract_date(item.get("expsEvntEndDt")) or self._extract_date(item.get("evntEndDt"))
        if not start or not end:
            return ""
        return f"{start}~{end}"

    def _extract_date(self, value: Any) -> str:
        normalized = normalize_text(str(value or ""))
        digits = re.sub(r"\D", "", normalized)
        if len(digits) < 8:
            return ""
        return f"{digits[:4]}.{digits[4:6]}.{digits[6:8]}"

    def _extract_label(self, value: Any) -> str:
        if isinstance(value, dict):
            return normalize_text(str(value.get("label") or ""))
        return normalize_text(str(value or ""))

    def _build_address(self, branch_code: str, floor: str, place: str) -> str:
        base = self._branches[branch_code].address
        location = self._compose_location_suffix(floor, place)
        if location:
            return f"{base} {location}"
        return base

    def _compose_location_suffix(self, floor: str, place: str) -> str:
        if floor in self._ignored_location_tokens:
            floor = ""
        if place in self._ignored_location_tokens:
            place = ""

        if floor and place:
            if floor in place:
                return place
            return f"{floor} {place}"
        return floor or place

    def _build_detail_url(self, branch_code: str, event_code: str) -> str:
        return (
            "https://www.ehyundai.com/newPortal/SN/SN_0201000.do"
            f"?evntCrdCd={event_code}&category=&page=1&branchCd={branch_code}"
        )
