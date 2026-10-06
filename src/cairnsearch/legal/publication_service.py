"""Application service for controlled legal-version publication."""

from __future__ import annotations

from uuid import UUID

from .models import VerificationStatus
from .publication_repository import LegalPublicationRepository
from .publishing import PublicationDraft
from .sources import validate_belarus_source_url


class LegalPublicationService:
    def __init__(self, repository: LegalPublicationRepository):
        self._repository = repository

    def publish(self, draft: PublicationDraft) -> UUID:
        if draft.version.verification_status != VerificationStatus.UNVERIFIED:
            raise ValueError("only UNVERIFIED drafts can be published")
        validate_belarus_source_url(draft.source_url)
        if draft.version.content_sha256 != __import__("hashlib").sha256(draft.source_content).hexdigest():
            raise ValueError("source content hash does not match legal version")
        return self._repository.publish(draft)
