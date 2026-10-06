"""Persistence contract for the controlled legal publication workflow."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from .models import LegalProvision, LegalVersion
from .publishing import PublicationDraft


class LegalPublicationRepository(Protocol):
    def publish(self, draft: PublicationDraft, *, source_url: str) -> UUID: ...
    def get_version(self, version_id: UUID) -> LegalVersion | None: ...
    def get_provision(self, version_id: UUID, locator: str) -> LegalProvision | None: ...
