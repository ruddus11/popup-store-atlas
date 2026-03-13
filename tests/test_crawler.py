from pathlib import Path

from crawler.adapters.marieclaire import MarieClaireAdapter
from crawler.adapters.tistory import TistoryAdapter
from crawler.models import RawPopupCandidate
from crawler.pipeline import normalize_candidate


def read_fixture(name: str) -> str:
    return Path("tests/fixtures", name).read_text(encoding="utf-8")


def test_marieclaire_adapter_extracts_structured_rows() -> None:
    adapter = MarieClaireAdapter()
    candidates = adapter.parse(
        read_fixture("marieclaire_sample.html"),
        "https://www.marieclairekorea.com/newnew/2025/02/sample-pop-up/",
    )

    assert len(candidates) == 2
    assert candidates[0].name == "AHC SKIN GAME T SHOT 팝업"
    assert candidates[0].address == "서울 성동구 연무장11길 13"
    assert candidates[0].raw_period == "2월 21일부터 3월 3일까지"


def test_tistory_adapter_extracts_addressed_items_only_after_normalization() -> None:
    adapter = TistoryAdapter()
    candidates = adapter.parse(
        read_fixture("tistory_sample.html"),
        "https://example.tistory.com/1",
    )

    accepted = []
    rejected = []
    for candidate in candidates:
        row, rejected_row = normalize_candidate(candidate)
        if row:
            accepted.append(row)
        if rejected_row:
            rejected.append(rejected_row)

    assert len(accepted) == 1
    assert accepted[0].name == "Soback 플래그십 스토어"
    assert len(rejected) == 1
    assert rejected[0].reason == "missing_name"


def test_tistory_adapter_recovers_known_venue_addresses_and_dedupes_summary_rows() -> None:
    adapter = TistoryAdapter()
    candidates = adapter.parse(
        read_fixture("tistory_alias_sample.html"),
        "https://example.tistory.com/aliases",
    )

    accepted = []
    for candidate in candidates:
        row, rejected_row = normalize_candidate(candidate)
        assert rejected_row is None
        assert row is not None
        accepted.append(row)

    assert len(accepted) == 3
    names = [row.name for row in accepted]
    addresses = [row.address for row in accepted]

    assert "더현대 서울 – K리그 × 주토피아 팝업" in names
    assert "서울 영등포구 여의대로 108 더현대 서울" in addresses
    assert "서울 용산구 한강대로23길 55 아이파크몰" in addresses
    assert "서울 성동구 연무장길" in addresses


def test_adapter_domain_matching_rejects_suffix_attack_hosts() -> None:
    adapter = MarieClaireAdapter()

    assert adapter.matches("https://www.marieclairekorea.com/article") is True
    assert adapter.matches("https://evilmarieclairekorea.com/article") is False


def test_normalize_candidate_rejects_untrusted_source_url() -> None:
    row, rejected = normalize_candidate(
        RawPopupCandidate(
            name="AHC",
            address="서울 성동구 연무장11길 13",
            raw_period="2025.02.21~2025.03.03",
            source_url="javascript:alert(1)",
            source_domain="marieclairekorea.com",
        )
    )

    assert row is None
    assert rejected is not None
    assert rejected.reason == "unsupported_source_scheme"
