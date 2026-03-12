#!/usr/bin/env bash
set -euo pipefail

DB_NAME="${1:-popup_db}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_PATH="${SCRIPT_DIR}/../sql/init_popup_db.sql"

if ! psql postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1; then
  createdb "${DB_NAME}"
fi

psql "${DB_NAME}" -v ON_ERROR_STOP=1 -f "${SQL_PATH}"

