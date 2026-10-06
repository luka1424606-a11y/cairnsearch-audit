"""Application service for controlled legal-version publication."""

from __future__ import annotations

from uuid import UUID

from .models import VerificationStatus
from .publication_repository import LegalPublicationRepository
from .publishing import PublicationDraft


class LegalPublicationService:
    def __init__(self, repository: LegalPublicationRepository):
        self._repository = repository

    def publish(self, draft: PublicationDraft, *, source_url: str) -> UUID:
        """Persist a complete draft and publish it atomically.

        The repository is responsible for a single database transaction:
        version + source snapshot + provisions + VERIFIED transition.
        """
        if draft.version.verification_status != VerificationStatus.UNVERIFIED:
            raise ValueError("only UNVERIFIED drafts can be published")
        return self._repository.publish(draft, source_url=source_url)
