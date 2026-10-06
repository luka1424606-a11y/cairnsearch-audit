"""PostgreSQL repository for internal documents."""

from __future__ import annotations

import secrets
from uuid import UUID

from sqlalchemy import text

from cairnsearch.platform.db import PostgresDatabase
from .models import Document, DocumentAccess, DocumentVersion


def _uuid() -> UUID:
    return UUID(int=secrets.randbits(128))


class PostgresDocumentRepository:
    def __init__(self, database: PostgresDatabase):
        self._database = database

    def get_document(self, organization_id: UUID, document_id: UUID) -> Document | None:
        sql = text("""SELECT id, organization_id, title, document_type, status, created_by
                      FROM internal_document
                      WHERE id=:document_id AND organization_id=:organization_id""")
        with self._database.connection() as conn:
            row = conn.execute(sql, {"document_id": document_id, "organization_id": organization_id}).mappings().first()
        if not row:
            return None
        return Document(row["id"], row["organization_id"], row["title"], row["document_type"], row["status"], row["created_by"])

    def get_latest_version(self, document_id: UUID) -> DocumentVersion | None:
        sql = text("""SELECT id, document_id, version_no, storage_key, content_sha256,
                             mime_type, byte_size, created_at
                      FROM internal_document_version
                      WHERE document_id=:document_id
                      ORDER BY version_no DESC LIMIT 1""")
        with self._database.connection() as conn:
            row = conn.execute(sql, {"document_id": document_id}).mappings().first()
        if not row:
            return None
        return DocumentVersion(row["id"], row["document_id"], row["version_no"], row["storage_key"],
                               row["content_sha256"], row["mime_type"], row["byte_size"], row["created_at"])

    def create_document(self, document: Document) -> None:
        with self._database.transaction() as conn:
            conn.execute(text("""INSERT INTO internal_document
                (id, organization_id, title, document_type, status, created_by)
                VALUES (:id,:organization_id,:title,:document_type,:status,:created_by)"""), {
                "id": document.id, "organization_id": document.organization_id,
                "title": document.title, "document_type": document.document_type,
                "status": document.status, "created_by": document.created_by})

    def create_version(self, version: DocumentVersion, created_by: UUID) -> None:
        with self._database.transaction() as conn:
            conn.execute(text("""INSERT INTO internal_document_version
                (id, document_id, version_no, storage_key, content_sha256,
                 mime_type, byte_size, created_by)
                VALUES (:id,:document_id,:version_no,:storage_key,:content_sha256,
                        :mime_type,:byte_size,:created_by)"""), {
                "id": version.id, "document_id": version.document_id,
                "version_no": version.version_no, "storage_key": version.storage_key,
                "content_sha256": version.content_sha256, "mime_type": version.mime_type,
                "byte_size": version.byte_size, "created_by": created_by})

    def can_read(self, user_id: UUID, organization_id: UUID, document_id: UUID) -> DocumentAccess:
        sql = text("""SELECT EXISTS (
            SELECT 1 FROM internal_document d
            JOIN internal_document_acl a ON a.document_id=d.id AND a.can_read=true
            JOIN user_role ur ON ur.role_id=a.role_id AND ur.user_id=:user_id
            WHERE d.id=:document_id AND d.organization_id=:organization_id)""")
        with self._database.connection() as conn:
            allowed = bool(conn.execute(sql, {"user_id":user_id,"organization_id":organization_id,"document_id":document_id}).scalar())
        return DocumentAccess(document_id, allowed, "ACL_ALLOW" if allowed else "ACL_DENY")

    def grant_role_read(self, document_id: UUID, role_id: UUID, actor_user_id: UUID) -> None:
        with self._database.transaction() as conn:
            conn.execute(text("""INSERT INTO internal_document_acl
                (id,document_id,role_id,can_read) VALUES (:id,:document_id,:role_id,true)
                ON CONFLICT (document_id,role_id) DO UPDATE SET can_read=true"""),
                {"id":_uuid(),"document_id":document_id,"role_id":role_id})
            conn.execute(text("""INSERT INTO internal_document_audit
                (id,document_id,actor_user_id,operation,details_json)
                VALUES (:id,:document_id,:actor_user_id,'ACL_GRANTED',:details)"""),
                {"id":_uuid(),"document_id":document_id,"actor_user_id":actor_user_id,
                 "details":'{"role_access":"read"}'})

    def revoke_role_read(self, document_id: UUID, role_id: UUID, actor_user_id: UUID) -> None:
        with self._database.transaction() as conn:
            conn.execute(text("""UPDATE internal_document_acl SET can_read=false
                                 WHERE document_id=:document_id AND role_id=:role_id"""),
                         {"document_id":document_id,"role_id":role_id})
            conn.execute(text("""INSERT INTO internal_document_audit
                (id,document_id,actor_user_id,operation,details_json)
                VALUES (:id,:document_id,:actor_user_id,'ACL_REVOKED',:details)"""),
                {"id":_uuid(),"document_id":document_id,"actor_user_id":actor_user_id,
                 "details":'{"role_access":"read"}'})

    def record_audit(self, document_id: UUID, version_id: UUID | None,
                     actor_user_id: UUID, operation: str, details_json: str | None = None) -> None:
        with self._database.transaction() as conn:
            conn.execute(text("""INSERT INTO internal_document_audit
                (id,document_id,version_id,actor_user_id,operation,details_json)
                VALUES (:id,:document_id,:version_id,:actor_user_id,:operation,:details_json)"""),
                {"id":_uuid(),"document_id":document_id,"version_id":version_id,
                 "actor_user_id":actor_user_id,"operation":operation,"details_json":details_json})
