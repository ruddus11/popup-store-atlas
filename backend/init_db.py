from __future__ import annotations

import argparse
import os
from pathlib import Path

import psycopg2


def default_database_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql:///popup_db")


def initialize_database(database_url: str, sql_path: Path) -> None:
    sql = sql_path.read_text(encoding="utf-8")
    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize popup database schema.")
    parser.add_argument("--database-url", default=default_database_url())
    parser.add_argument(
        "--sql-path",
        type=Path,
        default=Path("infra/sql/init_popup_db.sql"),
        help="Path to the SQL schema file.",
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    initialize_database(database_url=args.database_url, sql_path=args.sql_path)
    print(f"Initialized database using {args.sql_path}")


if __name__ == "__main__":
    main()

