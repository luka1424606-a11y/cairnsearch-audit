"""Persistence contract for legal publication workflow."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from .models import LegalProvision, LegalVersion


class LegalPublicationRepository(Protocol):
    def insert_unverified_version(self, version: LegalVersion, source_url: str, source_content: bytes) -> UUID: ...
    def insert_provisions(self, provisions: tuple[LegalProvision, ...]) -> None: ...
    def verify_version(self, version_id: UUID) -> None: ...
    def get_version(self, version_id: UUID) -> LegalVersion | None: ...
