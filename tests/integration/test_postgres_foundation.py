"""Real PostgreSQL integration tests.

Run with CAIRNSEARCH_DATABASE_URL pointing at a disposable test PostgreSQL
database. These tests intentionally do not substitute SQLite.
"""

from __future__ import annotations

import os
import uuid

import psycopg
import pytest


DATABASE_URL = os.getenv("CAIRNSEARCH_DATABASE_URL")

pytestmark = pytest.mark.integration


@pytest.fixture
def postgres_connection():
    if not DATABASE_URL:
        pytest.skip("CAIRNSEARCH_DATABASE_URL is not configured")
    with psycopg.connect(DATABASE_URL) as conn:
        yield conn


def test_postgres_connection_and_uuid_roundtrip(postgres_connection) -> None:
    value = uuid.uuid4()
    row = postgres_connection.execute("SELECT %s::uuid AS value", (value,)).fetchone()
    assert row[0] == value


def test_transaction_rolls_back(postgres_connection) -> None:
    table = f"_i1_test_{uuid.uuid4().hex}"
    try:
        with postgres_connection.transaction():
            postgres_connection.execute(f'CREATE TEMP TABLE "{table}" (id integer)')
            postgres_connection.execute(f'INSERT INTO "{table}" (id) VALUES (1)')
            raise RuntimeError("rollback")
    except RuntimeError:
        pass

    with pytest.raises(psycopg.errors.UndefinedTable):
        postgres_connection.execute(f'SELECT * FROM "{table}"')


def test_persistence_across_connection(postgres_connection) -> None:
    table = f"_i1_persist_{uuid.uuid4().hex}"
    postgres_connection.execute(f'CREATE TABLE "{table}" (id integer PRIMARY KEY)')
    postgres_connection.execute(f'INSERT INTO "{table}" (id) VALUES (1)')
    postgres_connection.commit()

    try:
        with psycopg.connect(DATABASE_URL) as second:
            row = second.execute(f'SELECT id FROM "{table}" WHERE id = 1').fetchone()
            assert row[0] == 1
    finally:
        postgres_connection.execute(f'DROP TABLE "{table}"')
        postgres_connection.commit()
