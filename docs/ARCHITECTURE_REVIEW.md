# ARCHITECTURE REVIEW — v1.0 → v1.1

Дата review: 2026-10-05

## Verdict

Архитектурная основа пригодна для перехода к детальному проектированию, но до передачи coding agent необходимо закрыть несколько внутренних неоднозначностей.

Критические замечания ниже исправляются в этой ветке. После исправлений целевой baseline получает статус v1.1.

## P0 — must fix before implementation

### P0-1. Evidence lineage is underspecified

Current DATA_MODEL allowed multiple nullable source foreign keys and only described "exactly one valid lineage" in prose. That is insufficient for DB integrity.

Decision:
Evidence has exactly one canonical owner:
- LEGAL_PROVISION, or
- INTERNAL_DOCUMENT_VERSION.

Official source/snapshot is reached through the legal provision's legal version. Internal source lineage is reached through internal document version.

Do not store redundant competing source foreign keys on evidence.

### P0-2. Document ACL target is ambiguous

"document_id" cannot safely refer to both legal and internal document tables.

Decision:
Use an explicit internal-document ACL table for sensitive company files.
Legal-source access is handled separately only if a future need is proven.

For current system:
internal_document_access.internal_document_id must have a real FK.

### P0-3. Legal applicability must not assume one valid version is always enough

A document can have amendments and provision-level changes. A simple "one version per date" rule is insufficient as a universal legal model.

Decision:
- keep legal_version validity intervals;
- add provision-level applicability/status overrides where source metadata requires it;
- implement an applicability resolver;
- allow resolver status: RESOLVED, NO_MATCH, AMBIGUOUS, CONFLICT;
- never silently prefer the newest version.

### P0-4. Final answers must not stream before validation

BUILD_SPECIFICATION exposes LLMGateway.stream(), but citation and claim validation happen after generation.

Decision:
- internal provider streaming is allowed;
- final user-visible answer is buffered until claim/citation/output policy validation completes;
- only safe progress/events may be streamed before final validation.

### P0-5. Provider/model administration is not yet specified

The system must allow changing external AI, but changing a provider/model is a privileged configuration action.

Decision:
- only ADMIN may create/modify/disable provider configurations;
- provider changes are audited;
- credentials are secret-managed;
- "test connection" must not send document content;
- model capability metadata is stored;
- per-agent model selection is supported later without changing agent logic.

### P0-6. Embedding model migration needs a first-class state

Changing embedding model must not silently invalidate old vectors.

Decision:
- embeddings carry provider/model/version/dimension;
- an embedding generation is identifiable;
- reindex creates the new generation;
- retrieval uses one compatible generation at a time;
- old generation can be retained until migration is verified, then retired.

## P1 — must be explicit

### P1-1. Authority ranking

Do not let the LLM invent source authority.

Decision:
source authority is structured metadata/policy, not a model judgment.

### P1-2. Local-only network policy

"Local-only" means at least no external LLM/embedding calls. It does not necessarily mean no Internet at all, because an explicit legal-source refresh may require outbound access.

Decision:
separate:
- llm_network_mode;
- embedding_network_mode;
- source_ingestion_network_mode;
- telemetry mode.

### P1-3. Public repository vs private application

The GitHub repository is currently public. Application data must never be committed to it.

Decision:
- no internal company documents;
- no personnel data;
- no API keys;
- no local database;
- no production snapshots

in Git.

### P1-4. Russian UI

Decision:
v1 user interface is Russian-language. Internal enum names may remain English; user-facing labels are Russian.

### P1-5. Retention

Exact legal/organizational retention periods are not invented here.

Decision:
retention policies are configurable and later grounded in verified Belarus requirements.

## P2 — later

- external identity/SSO;
- separate search engine;
- separate vector DB;
- complex workflow integrations;
- enterprise multi-tenancy beyond one organization.

## Review outcome

After P0/P1 amendments, architecture is internally coherent enough for detailed implementation specifications.

It is still not a statement that the application is legally compliant or production-ready. Legal requirements and provider terms must be separately verified.
