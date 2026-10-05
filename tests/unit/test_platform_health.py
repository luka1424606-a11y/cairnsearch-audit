from unittest.mock import Mock

from cairnsearch.platform.health import database_health


def test_database_health_ok() -> None:
    db = Mock()
    db.health_check.return_value = True

    assert database_health(db) == {"status": "ok"}


def test_database_health_unavailable() -> None:
    db = Mock()
    db.health_check.return_value = False

    assert database_health(db) == {"status": "unavailable"}
