# BUILD SPECIFICATION — target implementation contract v1.1

Этот документ предназначен для coding agent после утверждения TARGET_ARCHITECTURE.md.

Coding agent должен реализовывать систему по этим контрактам, а не самостоятельно заменять архитектуру.

## 1. Source of truth order

При конфликте:
1. TARGET_ARCHITECTURE.md
2. специализированная спецификация соответствующего домена
3. ADR
4. существующий cairnsearch code

Существующий code не имеет права переопределять новую архитектуру.

## 2. Required bounded contexts

- Identity & Access
- Organizations
- Documents
- Legal Knowledge
- Ingestion
- Retrieval
- Citations
- Policy
- Agents
- LLM Gateway
- Jobs
- Audit
- Storage
- Observability

## 3. Required interfaces

### AuthorizationService
check_user_permission(...)
check_document_access(...)
get_effective_scope(...)

### DocumentService
create_document(...)
create_version(...)
get_metadata(...)
get_authorized_content(...)
revoke_document(...)

### LegalKnowledgeService
get_document(...)
get_version_for_date(...)
get_provision(...)
publish_version(...)

### RetrievalService
search_exact(...)
search_lexical(...)
search_semantic(...)
search_hybrid(...)
build_evidence(...)

### CitationService
create_citation(...)
validate_citation(...)

### PolicyService
check_input(...)
check_retrieval(...)
check_tool(...)
check_output(...)

### LLMGateway
complete(...)
stream(...)
get_capabilities(...)
health(...)
get_usage(...)

Streaming is provider-internal. The application must buffer the final answer until claim validation, citation validation and output policy complete.

### Agent interface
handle(request) -> response

## 4. Dependency rules

Allowed:
API -> Application services -> Domain -> Infrastructure

Forbidden:
- Agent -> raw SQL
- Agent -> filesystem
- Agent -> arbitrary HTTP
- Agent -> secret store
- UI -> database
- LLM -> authorization
- Router -> access override

## 5. API security contract

Every protected route:
auth -> authorization -> validation -> operation -> audit.

Object access must be checked using authenticated principal and resource identity.

Sequential database IDs must not be treated as sufficient authorization.

## 6. Legal query contract

Required processing:
- jurisdiction;
- date context;
- authorized scope;
- retrieval;
- effective-period resolution;
- evidence sufficiency;
- citations;
- claims validation.

A legal answer without valid evidence cannot have SUPPORTED status.

## 7. Evidence contract

Evidence must include provenance and access verification.

No floating chunks.

Every evidence object must resolve back to:
source/document/version/provision or internal document version.

## 8. Citation contract

Citation generation is deterministic from evidence metadata.

LLM may reference evidence IDs; it does not author authoritative citation metadata.

## 9. LLM contract

Provider adapters must be interchangeable.

The core agent code cannot import a provider SDK directly.

Configuration includes provider/model, but secrets remain outside source.

Provider/model configuration is a privileged administrative operation and must be audited. Connection testing must never transmit document content.

## 10. Network-mode contract

Network controls are separate for:
- LLM provider;
- embedding provider;
- official-source ingestion;
- telemetry.

When local-only LLM mode is enabled, external LLM requests are blocked.
When local-only embedding mode is enabled, external embedding requests are blocked.
Source ingestion may remain separately permitted because updating an official source can require outbound network access.
Connection-test endpoints must follow the same network policy and must never send document content.

## 11. Legal-source publication contract

Only approved legal versions are published to production knowledge retrieval.

A raw fetched source or parsed candidate is not automatically authoritative.

## 12. Internal-document publication contract

Uploaded files begin in controlled processing/quarantine state.

Only successfully processed, authorized versions become retrieval-active.

## 13. Deletion contract

Legal published history cannot be deleted by ordinary users.

Internal document deletion/revocation invalidates future retrieval and dependent embeddings.

## 14. Audit contract

Every relevant operation contains:
request_id;
user_id;
organization_id;
action;
resource;
agent;
policy result;
source/evidence identifiers when applicable.

No secrets.

## 15. Error contract

User-facing errors are safe and actionable.

Internal details belong to protected logs.

Do not expose:
- stack trace;
- absolute internal filesystem path;
- SQL;
- secret values;
- internal network addresses.

## 16. Testing contract

No feature is accepted without applicable:
- unit tests;
- integration tests;
- authorization tests;
- negative tests.

Security-sensitive code additionally requires security regression tests.

## 17. Initial implementation boundary

First code should establish:
- PostgreSQL + migrations;
- identity/auth;
- RBAC/ACL;
- safe storage;
- legal domain;
- document domain;
- legal source snapshot model;
- retrieval interfaces;
- citation interfaces;
- policy engine interfaces;
- LLM gateway;
- agent registry.

Then implement real flows behind those interfaces.

## 18. Do not do

Do not:
- recreate the old SQLite system as the new backend;
- expose open-path endpoints;
- preserve destructive startup;
- make LLM directly control tools;
- allow retrieval before access filtering;
- generate unsupported legal citations;
- hard-code one LLM vendor into agent modules;
- introduce microservices merely for appearance;
- add a vector DB without benchmark justification;
- claim compliance based on UI presence.

## 19. Quality gate before merge

Required:
- migrations run cleanly;
- tests pass;
- security suite passes;
- no secrets found;
- no destructive startup;
- ACL enforced;
- legal provenance intact;
- citations validated;
- local-only mode verified;
- rollback/restore considerations documented.

## 20. Completion report

Coding agent must report:
- files changed;
- architecture deviations;
- tests run;
- tests not run;
- known limitations;
- unverified assumptions;
- security findings;
- remaining implementation gaps.

It must not report "production ready" unless every required P0 acceptance criterion is actually verified.
