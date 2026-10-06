"""HTTP boundary for internal documents.

All document operations follow: authentication -> permission -> object ACL ->
validation -> operation -> audit.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from cairnsearch.auth.dependencies import authenticated_principal
from cairnsearch.documents.authorization import DocumentAuthorizationService
from cairnsearch.documents.models import Document
from .application import DocumentApplicationService
from .repository import DocumentRepository

router = APIRouter(prefix="/documents", tags=["documents"])


def require_document_read(
    document_id: UUID,
    principal,
    authorization: DocumentAuthorizationService,
) -> Document:
    access = authorization.check_read(
        principal.user_id,
        principal.organization_id,
        document_id,
    )
    if not access.allowed:
        # Do not disclose whether a denied document exists.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    document = authorization._repository.get_document(
        principal.organization_id, document_id
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


async def upload_version(
    document_id: UUID,
    file: UploadFile,
    principal=Depends(authenticated_principal),
    document_service: DocumentApplicationService = Depends(),
    authorization: DocumentAuthorizationService = Depends(),
):
    document = require_document_read(document_id, principal, authorization)
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name required")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    return document_service.add_version(
        document,
        content,
        file.content_type or "application/octet-stream",
        principal.user_id,
    )
