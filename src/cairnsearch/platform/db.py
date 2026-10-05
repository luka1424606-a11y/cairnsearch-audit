"""PostgreSQL connection and transaction primitives."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg.rows import dict_row

from .config import PlatformConfig


class PostgresDatabase:
    """Small infrastructure wrapper; domain code must not use raw connections."""

    def __init__(self, config: PlatformConfig):
        self._config = config

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        with psycopg.connect(self._config.database_url, row_factory=dict_row) as conn:
            yield conn

    @contextmanager
    def transaction(self) -> Iterator[psycopg.Connection]:
        with psycopg.connect(self._config.database_url, row_factory=dict_row) as conn:
            with conn.transaction():
                yield conn

    def health_check(self) -> bool:
        try:
            with self.connection() as conn:
                conn.execute("SELECT 1").fetchone()
            return True
        except psycopg.Error:
            return False
