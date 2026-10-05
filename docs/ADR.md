# ARCHITECTURE DECISION RECORDS — v1.0

Все решения ниже относятся к целевой системе ИИ-агентов, а не к исходной реализации cairnsearch.

## ADR-001 — Modular monolith

Status: ACCEPTED

Decision:
Использовать модульный монолит как базовую архитектуру.

Reason:
- небольшая организация;
- три агента имеют общие сервисы;
- единая транзакционная БД;
- меньше инфраструктурной сложности;
- проще локальный запуск и приватное размещение;
- возможность позднего выделения сервисов без изменения доменных контрактов.

Rejected for initial build:
- microservice-first;
- autonomous swarm architecture.

Consequence:
Модули имеют четкие границы и не обходят application services.

## ADR-002 — PostgreSQL primary database

Status: ACCEPTED

Decision:
PostgreSQL является primary transactional database.

Reason:
- сильная транзакционная модель;
- structured relational data;
- access-control data;
- legal versioning;
- audit;
- возможность pgvector;
- full-text search.

Consequence:
Существующая SQLite schema cairnsearch не является целевой production schema.

## ADR-003 — pgvector initial vector layer

Status: ACCEPTED

Decision:
Использовать pgvector как initial vector layer.

Reason:
- vectors рядом с metadata;
- ACL/date/status filtering в одном data plane;
- меньше отдельных сервисов;
- проще private deployment.

Consequence:
Отдельная vector DB добавляется только при подтвержденной необходимости по benchmark.

## ADR-004 — PostgreSQL FTS for lexical retrieval

Status: ACCEPTED

Decision:
Использовать PostgreSQL Full Text Search как начальный lexical layer.

Reason:
- relational metadata;
- ranking;
- российская/русскоязычная configuration support;
- меньше инфраструктуры.

Caveat:
качество для белорусского юридического корпуса должно быть измерено.

## ADR-005 — Legal knowledge separated from internal documents

Status: ACCEPTED

Decision:
НПА и внутренние документы имеют разные domain entities и provenance.

Reason:
Правовой статус, lifecycle и access rules различаются.

Consequence:
Нельзя смешивать official legal evidence и internal company documents в одной сущности только потому, что оба представлены текстом.

## ADR-006 — Immutable published legal versions

Status: ACCEPTED

Decision:
Опубликованные legal versions immutable.

Reason:
Нужно сохранять историческую точность и provenance.

Consequence:
ошибка требует новой correction/revision record, а не скрытого overwrite.

## ADR-007 — Evidence and citation first

Status: ACCEPTED

Decision:
Ответ строится вокруг evidence и deterministic citation, а не вокруг свободной генерации LLM.

Reason:
юридический ответ должен быть проверяемым.

Consequence:
Claim without sufficient evidence cannot be presented as supported.

## ADR-008 — Explicit abstention

Status: ACCEPTED

Decision:
Недостаток доказательств является first-class system state.

Reason:
лучше явно отказать в подтверждении, чем генерировать правовой факт.

Consequence:
NOT_CONFIRMED / INSUFFICIENT_EVIDENCE / AMBIGUOUS are API states.

## ADR-009 — Provider-independent LLM gateway

Status: ACCEPTED

Decision:
LLM providers подключаются через adapter interface.

Reason:
не фиксировать систему навсегда на одном vendor; сохранить возможность local inference.

Consequence:
Agent modules не знают конкретный provider.

## ADR-010 — Private-first deployment

Status: ACCEPTED

Decision:
Система не требует public domain и public exposure.

Reason:
внутренние кадровые и юридические документы потенциально чувствительны.

Consequence:
локальный и private deployment являются первоклассными сценариями.

## ADR-011 — No autonomous legally significant actions

Status: ACCEPTED

Decision:
Агенты могут search/analyze/draft/cite/escalate, но не выполняют автономно юридически значимые действия.

Reason:
ошибки LLM не должны напрямую приводить к юридическому действию.

Consequence:
high-risk actions require explicit controlled application workflow and, where required, human approval.

## ADR-012 — Authorization before retrieval

Status: ACCEPTED

Decision:
ACL/access filtering is applied before evidence enters the agent/LLM context.

Reason:
после retrieval данные уже могут попасть в промежуточные слои.

Consequence:
LLM никогда не является last-mile access filter.

## ADR-013 — Local storage as initial object-storage implementation

Status: ACCEPTED

Decision:
Локальная файловая система является первой реализацией ObjectStorage interface.

Reason:
работает на одном компьютере;
не требует external cloud;
может позже быть заменена provider adapter.

Consequence:
business logic не зависит от path semantics.

## ADR-014 — No destructive startup

Status: ACCEPTED

Decision:
startup never deletes application data.

Reason:
исходный cairnsearch нарушает это правило через clear_all_data().

Consequence:
migrations are explicit and safe; destructive migration requires separate controlled procedure.

## ADR-015 — Bounded multi-domain orchestration

Status: ACCEPTED

Decision:
Multi-domain questions use a bounded orchestration flow rather than unrestricted agent recursion.

Reason:
контроль стоимости, безопасности, auditability.

Consequence:
maximum orchestration depth/steps must be explicit in implementation.

## ADR-016 — Conversation memory is not legal knowledge

Status: ACCEPTED

Decision:
Conversation history is not automatically promoted into authoritative knowledge.

Reason:
chat content is user-generated and may contain errors.

Consequence:
only approved knowledge-base objects are treated as authoritative evidence.

## ADR-017 — External-source ingestion requires explicit verification

Status: ACCEPTED

Decision:
Наличие URL не считается достаточным доказательством разрешенной автоматической загрузки.

Reason:
нужно отдельно подтвердить доступ, API, ограничения использования и metadata.

Consequence:
source connectors have explicit verification status and cannot silently become production ingestion.

