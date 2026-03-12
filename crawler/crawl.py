from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from crawler.adapters import ADAPTERS
from crawler.constants import CSV_HEADERS, REJECTED_HEADERS
from crawler.http import build_session, fetch_html
from crawler.io_utils import write_rows
from crawler.pipeline import normalize_candidate


def load_seed_urls(config_path: Path) -> list[str]:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        seed_urls = payload.get("seed_urls", [])
    else:
        seed_urls = payload
    return [str(url) for url in seed_urls]


def select_adapter(url: str):
    for adapter in ADAPTERS:
        if adapter.matches(url):
            return adapter
    raise ValueError(f"No adapter registered for {urlparse(url).netloc}")


def run_crawl(
    config_path: Path,
    output_path: Path,
    rejected_path: Path,
    timeout: int = 20,
) -> tuple[int, int]:
    session = build_session()
    accepted_rows: list[dict[str, str]] = []
    rejected_rows: list[dict[str, str]] = []

    for seed_url in load_seed_urls(config_path):
        adapter = select_adapter(seed_url)
        html = fetch_html(session, seed_url, timeout=timeout)
        candidates = adapter.parse(html, seed_url)
        for candidate in candidates:
            accepted, rejected = normalize_candidate(candidate)
            if accepted:
                accepted_rows.append(accepted.to_csv_row())
            if rejected:
                rejected_rows.append(rejected.to_csv_row())

    write_rows(output_path, CSV_HEADERS, accepted_rows)
    write_rows(rejected_path, REJECTED_HEADERS, rejected_rows)
    return len(accepted_rows), len(rejected_rows)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect popup store data into CSV.")
    parser.add_argument(
        "--config",
        default="crawler/config/seed_urls.json",
        type=Path,
        help="Path to the seed URL config JSON.",
    )
    parser.add_argument(
        "--output",
        default="data/interim/popup_stores.csv",
        type=Path,
        help="CSV output path for accepted rows.",
    )
    parser.add_argument(
        "--rejected-output",
        default="data/interim/rejected_rows.csv",
        type=Path,
        help="CSV output path for rejected rows.",
    )
    parser.add_argument("--timeout", default=20, type=int, help="HTTP timeout in seconds.")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    accepted_count, rejected_count = run_crawl(
        config_path=args.config,
        output_path=args.output,
        rejected_path=args.rejected_output,
        timeout=args.timeout,
    )
    print(f"Accepted rows: {accepted_count}")
    print(f"Rejected rows: {rejected_count}")


if __name__ == "__main__":
    main()

