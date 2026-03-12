from __future__ import annotations

from contextlib import contextmanager

import psycopg2


@contextmanager
def get_connection(database_url: str):
    connection = psycopg2.connect(database_url)
    try:
        yield connection
    finally:
        connection.close()

