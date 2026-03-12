from pathlib import Path

from crawler.adapters.marieclaire import MarieClaireAdapter
from crawler.adapters.tistory import TistoryAdapter
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
    assert rejected[0].reason == "missing_address"

