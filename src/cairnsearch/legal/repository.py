"""Persistence contracts for legal knowledge."""

from __future__ import annotations

from datetime import date
from typing import Protocol
from uuid import UUID

from .models import LegalDocument, LegalProvision, LegalResolution, LegalVersion, OfficialSource


class LegalRepository(Protocol):
    def get_document(self, jurisdiction: str, identifier: str) -> LegalDocument | None: ...
    def get_version(self, version_id: UUID) -> LegalVersion | None: ...
    def get_provision(self, version_id: UUID, locator: str) -> LegalProvision | None: ...
    def resolve_version(self, document_id: UUID, as_of: date) -> LegalResolution: ...
