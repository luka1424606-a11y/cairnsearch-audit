"""Application service enforcing citation eligibility."""

from __future__ import annotations

from .citation_repository import LegalCitationRepository
from .citations import LegalCitation, build_citation
from .models import LegalProvision, LegalVersion, SourceSnapshot, VerificationStatus


class LegalCitationService:
    def __init__(self, repository: LegalCitationRepository):
        self._repository = repository

    def create(
        self,
        *,
        version: LegalVersion,
        provision: LegalProvision,
        snapshot: SourceSnapshot,
    ) -> LegalCitation:
        if version.verification_status != VerificationStatus.VERIFIED:
            raise ValueError("only VERIFIED legal versions can be cited")
        citation = build_citation(version=version, provision=provision, snapshot=snapshot)
        self._repository.save(citation)
        return citation
