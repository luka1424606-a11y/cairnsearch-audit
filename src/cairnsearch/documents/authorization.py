"""Object-level authorization for internal documents."""

from __future__ import annotations

from uuid import UUID

from cairnsearch.authorization.service import AuthorizationService
from .models import DocumentAccess
from .repository import DocumentRepository


class DocumentAuthorizationService:
    def __init__(self, repository: DocumentRepository, authorization: AuthorizationService):
        self._repository = repository
        self._authorization = authorization

    def get_document(self, organization_id: UUID, document_id: UUID):
        return self._repository.get_document(organization_id, document_id)

    def check_read(self, user_id: UUID, organization_id: UUID, document_id: UUID) -> DocumentAccess:
        document = self._repository.get_document(organization_id, document_id)
        if document is None:
            return DocumentAccess(document_id, False, "DOCUMENT_NOT_FOUND")
        acl = self._repository.can_read(user_id, organization_id, document_id)
        if not acl.allowed:
            return acl
        return self._authorization.check_document_access(user_id, organization_id, document_id, True)
