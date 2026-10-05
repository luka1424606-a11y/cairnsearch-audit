# DATA MODEL — целевая модель данных v1.0

## 1. Назначение

Этот документ детализирует модель данных целевой корпоративной системы.

Цель — обеспечить:
- однозначную идентификацию объектов;
- неизменяемую историю юридических редакций;
- provenance;
- effective periods;
- document ACL;
- citations;
- audit;
- отсутствие orphan-записей.

## 2. Принцип владения данными

Каждая сущность должна иметь явного владельца доменной логики.

- Identity/organization — identity module.
- Legal documents — legal module.
- Internal documents — document module.
- Evidence/citations — retrieval/citation modules.
- Audit — audit module.
- Embeddings — retrieval infrastructure.

Агентам запрещён прямой доступ к таблицам.

## 3. Идентификаторы

Использовать UUID/UUID-compatible identifiers для доменных сущностей.

Не использовать последовательный integer ID как внешний публичный идентификатор чувствительных объектов.

Внутренние технические surrogate keys допустимы только там, где они не раскрываются наружу.

## 4. Organization

organization:
- id
- name
- legal_name
- jurisdiction
- created_at
- updated_at
- status

Для данной системы:
jurisdiction = BY по умолчанию.

## 5. User

user:
- id
- organization_id
- login
- display_name
- password_hash или external_identity
- status
- created_at
- updated_at
- last_login_at

Пароли никогда не хранятся в plaintext.

## 6. Role

role:
- id
- code
- name
- description

Initial roles:
ADMIN
LEGAL
HR
OCCUPATIONAL_SAFETY
EMPLOYEE

## 7. Permission

permission:
- id
- code
- description

Role-permission mapping:
role_permissions.

Пользователь может иметь несколько ролей только если это явно разрешено политикой организации.

## 8. Document ACL

document_access:
- id
- document_id
- subject_type
- subject_id
- permission
- granted_by
- created_at
- revoked_at

subject_type:
- USER
- ROLE
- ORGANIZATION

Default deny.

Приоритеты конфликтующих правил должны быть формализованы до реализации.

## 9. LegalDocument

legal_document:
- id
- legal_system
- document_type
- title
- short_title
- issuing_body
- registration_number
- adoption_date
- official_publication_reference
- status
- created_at
- updated_at

legal_system = BY для белорусских НПА.

## 10. LegalVersion

legal_version:
- id
- legal_document_id
- version_identifier
- publication_date
- valid_from
- valid_to
- status
- snapshot_id
- content_hash
- parser_version
- verification_status
- approved_by
- approved_at
- created_at

Published legal versions are immutable.

Исправление ошибки должно создавать новую revision/snapshot, а не silently overwrite published history.

## 11. LegalProvision

legal_provision:
- id
- legal_version_id
- parent_id
- provision_type
- ordinal
- label
- text
- normalized_text
- source_locator
- page_number
- start_offset
- end_offset
- created_at

provision_type may be:
SECTION
CHAPTER
ARTICLE
PART
ITEM
SUBITEM
PARAGRAPH
OTHER

## 12. LegalSource

official_source:
- id
- source_name
- jurisdiction
- canonical_url
- source_type
- official_status
- retrieval_method
- verification_status
- created_at
- updated_at

## 13. SourceSnapshot

source_snapshot:
- id
- official_source_id
- retrieved_at
- canonical_url
- content_hash
- media_type
- storage_ref
- parser_version
- integrity_status
- metadata_json

Raw snapshot is immutable.

## 14. InternalDocument

internal_document:
- id
- organization_id
- document_type
- title
- owner_user_id
- classification
- status
- created_at
- updated_at

classification is a business field and must not be treated as a security decision by itself.

## 15. InternalDocumentVersion

internal_document_version:
- id
- internal_document_id
- version_number
- effective_from
- effective_to
- file_object_id
- content_hash
- parser_version
- processing_status
- created_by
- created_at

Version history is retained according to organization policy.

## 16. FileObject

file_object:
- id
- storage_backend
- storage_key
- original_filename
- media_type
- size_bytes
- content_hash
- created_at
- deletion_state

Application never stores an arbitrary user-supplied filesystem path as an authorization identity.

## 17. ProcessingJob

processing_job:
- id
- job_type
- object_id
- state
- attempt_count
- max_attempts
- idempotency_key
- created_at
- started_at
- completed_at
- error_code
- error_message

## 18. Evidence

evidence:
- id
- source_type
- official_source_id nullable
- legal_document_id nullable
- legal_version_id nullable
- legal_provision_id nullable
- internal_document_id nullable
- internal_document_version_id nullable
- chunk_id nullable
- text
- locator_json
- temporal_validity
- access_verified
- retrieval_metadata_json
- created_at

Exactly one valid source lineage must be resolvable for each evidence item.

## 19. Embedding

embedding:
- id
- evidence_id
- model_provider
- model_name
- model_version nullable
- vector
- vector_dimension
- created_at

Embedding rows are dependent on their evidence parent.

## 20. Citation

citation:
- id
- evidence_id
- citation_type
- label
- rendered_text
- locator_json
- created_at

A citation cannot exist without valid evidence.

## 21. Conversation

conversation:
- id
- user_id
- agent_code
- created_at
- updated_at
- status

conversation_message:
- id
- conversation_id
- role
- content
- created_at

Do not treat conversation messages as legal source material automatically.

## 22. AgentRun

agent_run:
- id
- conversation_id
- request_id
- agent_code
- provider
- model
- policy_version
- started_at
- completed_at
- status

## 23. Claim

claim:
- id
- agent_run_id
- text
- claim_type
- validation_status

claim_evidence:
- claim_id
- evidence_id
- support_strength
- validator_version

## 24. AuditEvent

audit_event:
- id
- timestamp
- organization_id
- user_id
- request_id
- action
- resource_type
- resource_id
- agent_code
- decision
- policy_version
- model_provider
- model_name
- metadata_json

Audit records must be append-only for normal application roles.

## 25. Constraints

Critical DB constraints:
- foreign keys enabled;
- unique version identifiers per document;
- unique source snapshot hash where appropriate;
- no citation without evidence;
- no embedding without evidence;
- no legal provision without legal version;
- no legal version without legal document and source lineage;
- no internal document version without internal document;
- no ACL without existing document;
- audit rows cannot be updated/deleted by ordinary users.

## 26. Transaction boundaries

Publication of a legal version should be transactional for:
- version;
- provisions;
- publication status;
- searchable metadata.

Embedding/index creation can be asynchronous, but publication status must not claim searchable completeness until required indexing completes.

## 27. Deletion rules

Legal history:
- no ordinary deletion.

Internal document:
- logical deletion/revocation first;
- dependent retrieval records must be removed or invalidated;
- physical deletion only under explicit policy.

## 28. Data integrity

Every ingestion path must preserve:
source -> document -> version -> provision -> evidence -> citation lineage.

No transformation may discard the identity needed to reconstruct provenance.

