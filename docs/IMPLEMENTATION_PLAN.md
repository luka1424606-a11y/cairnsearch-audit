# IMPLEMENTATION PLAN — target architecture v1.1

Статус: approved implementation sequence
Branch: architecture/target-v1

## 1. Правило

Реализация выполняется только после архитектурного baseline v1.1.

Каждая итерация должна:
- соответствовать TARGET_ARCHITECTURE.md;
- не создавать временную архитектуру, которую затем придется выбрасывать;
- иметь реальные tests;
- не внедрять секреты;
- не менять main без отдельного merge/review.

## 2. Workstream order

Dependencies require the following order:

I0 — Repository baseline and safety
I1 — Database foundation
I2 — Identity, authentication, RBAC
I3 — Internal document and storage domain
I4 — Legal knowledge domain
I5 — Ingestion and processing
I6 — Retrieval and embeddings
I7 — Evidence, citations and validation
I8 — Policy engine and LLM Gateway
I9 — Agent registry and three agents
I10 — Router and bounded multi-domain orchestration
I11 — Web UI and complete user flows
I12 — Security hardening
I13 — Evaluation
I14 — Backup/restore and deployment
I15 — Final acceptance

Не пропускать зависимости. Не строить UI как замену отсутствующей backend functionality.

## 3. I0 — Repository baseline and safety

Goals:
- freeze architecture docs;
- inspect all current startup paths;
- remove/disable destructive startup in the target implementation;
- define clean package boundaries;
- establish migration framework;
- establish test runner and linting.

Acceptance:
- application startup cannot delete data;
- architecture docs available in branch;
- baseline tests runnable;
- no production code yet depends on the old SQLite schema as the target persistence model.

## 4. I1 — Database foundation

Implement:
- PostgreSQL connection layer;
- migrations;
- transaction boundaries;
- UUID identifiers;
- organization/user-independent schema foundation;
- audit table foundation;
- required extensions including pgvector if available in deployment.

Acceptance:
- clean migration;
- repeat migration is safe;
- DB restart retains data;
- invalid migration does not silently destroy data.

## 5. I2 — Identity, authentication and authorization

Implement:
- organization;
- user;
- role;
- permissions;
- role-permission mapping;
- server-side sessions;
- password hashing;
- authentication middleware;
- authorization service;
- default-deny.

Acceptance:
- login/logout;
- session expiry;
- role-based endpoint protection;
- object-level permission checks;
- authorization tests;
- privilege-change tests.

## 6. I3 — Internal document and storage domain

Implement:
- FileObject;
- InternalDocument;
- InternalDocumentVersion;
- InternalDocumentAccess;
- object storage interface;
- local filesystem storage adapter;
- upload/quarantine lifecycle.

Acceptance:
- users can upload only when permitted;
- arbitrary filesystem paths are never accepted as storage identity;
- ACL is enforced before content retrieval;
- logical revocation prevents future retrieval.

## 7. I4 — Legal knowledge domain

Implement:
- LegalDocument;
- LegalVersion;
- LegalProvision;
- OfficialSource;
- SourceSnapshot;
- document relations;
- effective-period resolver;
- verification/approval states.

Acceptance:
- legal version is immutable after publication;
- a version can be resolved by date;
- no source lineage is lost;
- ambiguous date resolution is represented as an explicit state.

## 8. I5 — Ingestion and processing

Implement:
- source connector interface;
- internal document parser pipeline;
- legal source parser pipeline;
- hash/integrity;
- parser version;
- quarantine;
- background jobs;
- retry/idempotency;
- safe extractor isolation.

Acceptance:
- duplicate ingestion is idempotent;
- parser failures quarantine correctly;
- hash mismatch blocks publication;
- published legal source requires approval;
- no secrets reach extractor subprocesses.

## 9. I6 — Retrieval and embeddings

Implement:
- exact search;
- PostgreSQL FTS;
- semantic retrieval;
- EvidenceCandidate;
- hybrid merge;
- temporal filtering;
- ACL filtering;
- embedding generations.

Acceptance:
- authorized scope is resolved before retrieval;
- no forbidden evidence reaches the agent;
- changing embedding model creates a new generation;
- retrieval results have provenance;
- no orphan embeddings.

## 10. I7 — Evidence, citations and validation

Implement:
- Evidence model;
- Citation Service;
- Claim model;
- claim/evidence mapping;
- citation validation;
- answer statuses;
- abstention.

Acceptance:
- citation is generated only from evidence;
- unsupported material claim cannot have SUPPORTED status;
- stale/invalid citation is rejected;
- internal document is never displayed as official law;
- final response is buffered until validation is complete.

## 11. I8 — Policy engine and LLM Gateway

Implement:
- ProviderAdapter interface;
- LLMGateway;
- model/provider configuration;
- secret handling;
- network-mode policy;
- local provider adapter;
- cloud provider adapter(s) only when explicitly configured;
- usage metadata.

Acceptance:
- core agent code has no provider SDK dependency;
- provider can be changed by admin configuration;
- provider change is audited;
- local-only mode blocks cloud LLM/embedding requests;
- connection test does not send document content;
- streaming is internal only until final validation.

## 12. I9 — Agent registry and agents

Implement:
- common Agent interface;
- policy versions;
- LegalAgent;
- HRAgent;
- OccupationalSafetyAgent;
- agent-specific tool allowlists;
- high-risk action policy;
- escalation payloads.

Acceptance:
- each agent works through shared infrastructure;
- each agent only receives authorized evidence;
- high-risk actions cannot execute autonomously;
- agent policy version recorded per run.

## 13. I10 — Router and multi-domain orchestration

Implement:
- deterministic routing rules;
- optional model-assisted classification behind policy;
- bounded orchestration;
- primary/secondary domains.

Acceptance:
- routing failure does not bypass authorization;
- no recursive uncontrolled agent chain;
- maximum steps are enforced;
- all sub-operations are auditable.

## 14. I11 — Web UI

Implement:
- login;
- home;
- agent selection;
- conversation;
- evidence/citation display;
- document management;
- legal source management for privileged roles;
- administration;
- status/warnings/escalation display.

Acceptance:
- UI never hides a security failure;
- backend remains authoritative for permissions;
- user sees Russian labels;
- final answer shows evidence status and citations.

## 15. I12 — Security hardening

Run and fix:
- IDOR;
- privilege escalation;
- session attacks;
- CSRF where applicable;
- CORS;
- path traversal;
- unsafe upload;
- parser abuse;
- prompt injection;
- secret leakage;
- unexpected network egress;
- security headers;
- rate limiting where needed.

Acceptance:
all P0/P1 security tests pass.

## 16. I13 — Quality and retrieval evaluation

Create:
- legal test corpus;
- internal test corpus;
- question set;
- date-dependent set;
- no-answer set;
- conflict set;
- citation set.

Measure:
- Recall@k;
- Precision@k;
- MRR;
- NDCG;
- citation accuracy;
- unsupported claim rate;
- correct abstention rate;
- latency.

Acceptance:
thresholds are data-derived and documented. No invented universal threshold.

## 17. I14 — Backup, restore and deployment

Implement:
- backup;
- restore;
- health checks;
- configuration separation;
- deployment packaging;
- local deployment;
- private server deployment documentation.

Acceptance:
- backup exists;
- restore test passes;
- application restarts without data loss;
- no public domain is required for local/private mode.

## 18. I15 — Final acceptance

A release candidate is accepted only if:
- all required tests pass;
- no destructive startup exists;
- auth/RBAC/ACL work;
- legal provenance works;
- version resolver works;
- retrieval ACL works;
- citations validate;
- unsupported claims abstain;
- model switching works;
- local-only network policy works;
- audit is complete;
- backup/restore verified;
- known gaps are documented.

## 19. Implementation discipline

Coding agent must:
- read the architecture documents before changing code;
- inspect current code before replacing a module;
- reuse existing components only after security/domain review;
- avoid broad rewrites without test coverage;
- report deviations;
- never invent an API contract that was not verified;
- never claim a component works unless it was executed/tested.

## 20. Merge discipline

Each implementation iteration should be a reviewable commit/PR-sized unit.

No direct push to main.

Architecture branch remains the review baseline until implementation is accepted.

## 21. First implementation target

The first actual code milestone is not an agent chat.

It is:

PostgreSQL
+ migrations
+ identity
+ authorization
+ safe document storage
+ legal data model
+ test infrastructure.

Only after this foundation is working should agent behavior be connected.

