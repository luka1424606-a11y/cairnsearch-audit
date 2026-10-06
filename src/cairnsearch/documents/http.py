"""HTTP boundary for internal documents.

All document operations follow:
authentication -> operation permission -> object ACL -> validation -> operation -> audit.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, UploadFile, status

from cairnsearch.auth.dependencies import authenticated_principal
from .authorization import DocumentAuthorizationService

router = APIRouter(prefix="/documents", tags=["documents"])


def require_document_read(document_id: UUID, principal, authorization: DocumentAuthorizationService):
    access = authorization.check_read(principal.user_id, principal.organization_id, document_id)
    if not access.allowed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    document = authorization.get_document(principal.organization_id, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


async def upload_version(
    document_id: UUID,
    file: UploadFile,
    request: Request,
):
    principal = authenticated_principal(request)
    authz = getattr(request.app.state, "document_authorization", None)
    service = getattr(request.app.state, "document_service", None)
    authorization_service = getattr(request.app.state, "authorization_service", None)

    if authz is None or service is None or authorization_service is None:
        raise HTTPException(status_code=503, detail="Document service unavailable")

    try:
        authorization_service.require_permission(
            principal.user_id,
            principal.organization_id,
            "documents.manage",
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail="Forbidden") from exc

    document = require_document_read(document_id, principal, authz)
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name required")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    return service.add_version(
        document,
        content,
        file.content_type or "application/octet-stream",
        principal.user_id,
    )
