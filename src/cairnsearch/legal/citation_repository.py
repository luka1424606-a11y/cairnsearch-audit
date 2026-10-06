"""Persistence contract for deterministic legal citations."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from .citations import LegalCitation


class LegalCitationRepository(Protocol):
    def save(self, citation: LegalCitation) -> None: ...
    def get_by_key(self, citation_key: str) -> LegalCitation | None: ...
    def get_for_provision(self, provision_id: UUID) -> LegalCitation | None: ...
