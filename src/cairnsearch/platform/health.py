"""Database health service."""

from .db import PostgresDatabase


def database_health(db: PostgresDatabase) -> dict[str, str]:
    healthy = db.health_check()
    return {"status": "ok" if healthy else "unavailable"}
