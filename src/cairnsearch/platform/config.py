"""Configuration for the target platform foundation."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformConfig:
    """Minimal, secret-free runtime configuration."""

    database_url: str
    app_env: str = "dev"
    enable_pgvector: bool = True

    @classmethod
    def from_env(cls) -> "PlatformConfig":
        database_url = os.getenv("CAIRNSEARCH_DATABASE_URL")
        if not database_url:
            raise RuntimeError(
                "CAIRNSEARCH_DATABASE_URL is required for the target PostgreSQL backend"
            )
        return cls(
            database_url=database_url,
            app_env=os.getenv("CAIRNSEARCH_ENV", "dev"),
            enable_pgvector=os.getenv("CAIRNSEARCH_ENABLE_PGVECTOR", "true").lower()
            in {"1", "true", "yes", "on"},
        )
