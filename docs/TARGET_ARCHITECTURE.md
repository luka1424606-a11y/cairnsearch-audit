# Target Architecture — корпоративная система ИИ-агентов для Республики Беларусь

Статус: целевая архитектура v1.0
Ветка: architecture/target-v1
Назначение: основной технический документ для последующей реализации системы.

## 0. Правила документа

Документ разделяет:
1. Подтверждено — установлено по текущему репозиторию, сохраненному аудиту или официальным техническим источникам.
2. Архитектурное решение — решение для целевой системы.
3. Требует отдельной проверки — вопрос, который нельзя закрыть без проверки конкретного API, лицензии, юридического требования, провайдера или deployment.

Нельзя превращать статус «требует проверки» в реализованный факт.

## 1. Цель

Создать единую корпоративную систему для небольшой организации в Республике Беларусь, до 10 сотрудников, с тремя специализированными агентами:
- Юридический агент.
- Кадровый агент.
- Агент по охране труда.

Система предназначена для:
- поиска;
- анализа;
- подготовки проектов;
- проверки внутренних документов по подтвержденным требованиям;
- формирования ответов с доказуемыми источниками;
- фиксации истории действий.

Система не является автономным субъектом принятия юридически значимых решений.

Главный принцип:
ИИ не является источником права. Источниками являются проверенные документы и нормы. ИИ обрабатывает отобранные доказательства.

## 2. Что именно строим

Это не три независимых чат-бота, а одна платформа.

Поток:
Пользователь
→ аутентификация
→ авторизация
→ Router
→ специализированный агент
→ Policy / Safety
→ Retrieval
→ Evidence
→ LLM Gateway
→ Claim / Citation validation
→ Final Policy
→ ответ
→ Audit

Три агента используют общую инфраструктуру:
- auth;
- access control;
- legal knowledge base;
- document service;
- retrieval;
- citations;
- policy;
- audit;
- LLM Gateway.

Они не имеют трех копий одной юридической базы.

## 3. Границы системы

Входит:
- учетные записи;
- аутентификация;
- RBAC;
- ACL документов;
- аудит;
- юридическая база;
- версии НПА;
- effective periods;
- provenance;
- internal documents;
- document versioning;
- exact/lexical/semantic/hybrid search;
- evidence;
- citations;
- claim validation;
- abstention;
- три агента;
- заменяемый LLM provider;
- фоновые задания;
- резервирование;
- восстановление;
- тестирование;
- приватное размещение.

Не является обязательным:
- публичный маркетинговый сайт;
- публичный доступ;
- собственный домен;
- мобильное приложение;
- Google Drive;
- один конкретный LLM provider;
- отдельный vector database;
- autonomous multi-agent swarm;
- автоматическая отправка официальных документов;
- автономное изменение юридических записей.

## 4. Размещение

Сейчас у владельца проекта нет собственного сервера, закрытой корпоративной сети и домена.

Поэтому приложение проектируется независимо от конкретной инфраструктуры.

Поддерживаются:
A. DEV / SINGLE MACHINE — локальный запуск на одном компьютере.
B. PRIVATE SERVER — выделенный сервер с ограниченным сетевым доступом.
C. FUTURE CLOUD — арендованная облачная инфраструктура с приватным доступом.

Публичный домен не является архитектурной зависимостью.

## 5. Состояние исходного репозитория

Репозиторий:
luka1424606-a11y/cairnsearch-audit

Ветка main существует, репозиторий в текущем подключении виден и доступен на чтение/запись.

Текущий main содержит исходный код cairnsearch, SQLite, FTS5, RAG, OCR/extractors, security-модули, web UI и документы SCHEMA.md и REVIEWER_RESPONSE.md.

В текущем main отсутствуют ранее обсуждавшиеся отдельные архитектурные документы с именами belarus-legal-sources.md, legal-data-model.md, database-design.md и др. Поэтому этот документ фиксирует целевую архитектуру непосредственно в репозитории.

Важное правило:
текущий cairnsearch рассматривается как технический донор модулей, а не как production-архитектура новой системы.

## 6. Критические дефекты текущего кода

Текущий src/cairnsearch/api/app.py содержит clear_all_data(), которая удаляет каталог данных при старте.

Это запрещено в целевой системе.

Запуск новой системы должен быть идемпотентным:
startup
→ check schema
→ safe migrations
→ initialize services

а не:
startup
→ delete data.

Текущий API также содержит операции открытия файлов по произвольному пути и другие функции, которые нельзя переносить в production без новой security boundary.

## 7. Модель приложения

Целевой стиль:
модульный монолит.

Логические модули:
- api
- auth
- authorization
- users
- organizations
- agents/legal
- agents/hr
- agents/occupational_safety
- routing
- policy
- retrieval
- legal
- documents
- ingestion
- citations
- llm
- storage
- audit
- jobs
- search
- database
- observability
- web

Агент не должен напрямую выполнять SQL, читать произвольный путь файловой системы, получать секреты или самостоятельно обходить ACL.

## 8. Основные классы данных

Разделить:
1. нормативные источники и НПА;
2. внутренние документы организации;
3. пользовательские запросы и ответы;
4. аудит.

НПА и внутренний документ могут оба содержать текст, но это разные типы источников.

## 9. Юридическая модель

Основные сущности:

legal_documents
- сущность НПА;
- legal_system = BY;
- тип;
- название;
- орган принятия;
- регистрационный номер;
- даты;
- официальная публикация;
- статус.

legal_versions
- конкретная редакция;
- идентификатор редакции;
- valid_from;
- valid_to;
- дата публикации;
- snapshot;
- content hash;
- verification status.

legal_provisions
- структурированная норма;
- parent provision;
- тип элемента;
- порядковый номер;
- подпись;
- normalized text;
- locator.

Поддерживаемая иерархия:
раздел → глава → статья → часть → пункт → подпункт → абзац.

Не каждый НПА обязан иметь все уровни.

## 10. Effective periods

На запрос с датой система должна определить редакцию, применимую на эту дату.

Алгоритм:
document
→ candidate versions
→ filter by validity interval
→ resolve status
→ if exactly one confirmed candidate, use it
→ if zero, insufficient evidence
→ if several conflicting candidates, ambiguous.

Запрещено выбирать «последний загруженный файл» только на основании времени загрузки.

## 11. Официальные источники

Создается official_sources.

Минимум:
- source_id;
- source_name;
- jurisdiction;
- canonical_url;
- source_type;
- official_status;
- retrieval_method;
- verification_status;
- notes.

На текущем уровне подтверждены официальные правовые ресурсы:
- Национальный правовой Интернет-портал Республики Беларусь, pravo.by;
- ЭТАЛОН-ONLINE / ресурсы НЦЗПИ.

Для каждого источника отдельной проверкой устанавливаются:
- способ доступа;
- наличие API;
- допустимый способ получения;
- ограничения использования;
- частота обновления;
- полнота метаданных.

Наличие URL само по себе не подтверждает возможность автоматической массовой выгрузки.

## 12. Source snapshots

Каждое полученное внешнее юридическое содержимое фиксируется как snapshot.

Snapshot:
- source_id;
- retrieved_at;
- canonical_url;
- raw payload reference;
- content hash;
- media type;
- parser version;
- integrity status.

Snapshot нужен для последующей проверки происхождения данных.

## 13. Legal ingestion pipeline

SOURCE REGISTRY
→ FETCH
→ RAW SNAPSHOT
→ HASH / INTEGRITY
→ PARSE
→ STRUCTURE
→ NORMALIZE
→ METADATA VALIDATION
→ LEGAL REVIEW / APPROVAL
→ PUBLISH
→ INDEX

Автоматическое получение и публикация — разные стадии.

Юридически значимый источник не становится частью опубликованной knowledge base только потому, что файл успешно скачался и распарсился.

## 14. Internal document pipeline

UPLOAD
→ AUTHORIZATION
→ FILE VALIDATION
→ QUARANTINE
→ HASH
→ SAFE STORAGE
→ EXTRACTION / OCR
→ QUALITY CHECK
→ METADATA
→ VERSION
→ INDEX

Факт загрузки файла не означает, что агенту уже разрешено его использовать.

## 15. Storage abstraction

Бизнес-логика не должна зависеть от конкретного storage provider.

Интерфейс:
- put;
- get;
- delete;
- exists;
- metadata.

Первая реализация:
локальная файловая система.

Позже допускается S3-compatible storage или другой provider без изменения Document Service.

## 16. PostgreSQL

Целевая primary database:
PostgreSQL.

В БД размещаются:
- users;
- organizations;
- roles;
- permissions;
- document ACL;
- legal documents;
- legal versions;
- legal provisions;
- source metadata;
- snapshots metadata;
- internal documents;
- document versions;
- jobs;
- citations;
- audit metadata;
- embeddings.

PostgreSQL Row-Level Security может использоваться как дополнительный защитный слой. При включенном RLS и отсутствии подходящей политики PostgreSQL применяет default-deny. Это не заменяет application-level authorization.

## 17. PostgreSQL security baseline

На момент подготовки документа PostgreSQL сообщил CVE-2026-14666, связанный с кэшированием row-security policies; исправленные patch-level версии включают 18.6, 17.11, 16.15, 15.19 и 14.24.

Production deployment не должен использовать затронутые более старые patch-level версии.

Целевой baseline:
PostgreSQL 18.6+ или более новая поддерживаемая исправленная версия, выбранная на момент deployment review.

## 18. Vector layer

Целевой initial vector layer:
pgvector.

Причины:
- embeddings рядом с metadata;
- совместная фильтрация по access/date/status;
- меньше отдельных сервисов;
- один primary data plane.

pgvector поддерживает exact nearest-neighbor search, а также HNSW и IVFFlat для approximate search.

HNSW не включается автоматически. Нужен retrieval benchmark на реальном корпусе.

## 19. Lexical search

Целевой lexical search:
PostgreSQL Full Text Search.

Для русского PostgreSQL предоставляет russian text-search configuration.

Но это не является доказательством качества белорусского юридического поиска.

Поэтому поиск должен быть протестирован на реальных русскоязычных и белорусскоязычных юридических запросах.

## 20. Три уровня поиска

1. Exact:
- номер НПА;
- статья;
- пункт;
- дата;
- название;
- exact phrase.

2. Lexical:
- обычный текстовый поиск;
- морфологически устойчивый поиск, насколько позволяет выбранная конфигурация.

3. Semantic:
- поиск по embeddings.

Результаты всех трёх методов приводятся к одному EvidenceCandidate.

## 21. Hybrid retrieval

Каждый кандидат должен быть одного уровня — provision/chunk, а не смешение document-level и chunk-level.

EvidenceCandidate:
- evidence_id;
- source_type;
- source_id;
- document_id;
- version_id;
- provision_id;
- chunk_id;
- text;
- locator;
- lexical_score;
- semantic_score;
- temporal_validity;
- authority;
- access_verified.

Текущий hybrid retriever cairnsearch использует несовпадающие уровни результата, поэтому его логику нельзя переносить как есть.

## 22. Retrieval order

Для legal query:
1. определить область;
2. определить дату;
3. определить юрисдикцию;
4. ограничить документы по ACL;
5. exact search;
6. lexical search;
7. semantic search;
8. merge;
9. temporal/status filter;
10. ranking;
11. evidence set;
12. evidence sufficiency check.

## 23. Evidence

Evidence — первичный объект, с которым работает агент.

Содержит:
- источник;
- документ;
- редакцию;
- норму;
- период действия;
- текст;
- locator;
- страницу/область, если доступны;
- retrieval scores;
- проверку доступа.

Агент получает только authorized evidence.

## 24. Citation service

Citation — отдельный сервис.

Цепочка:
Claim
→ Evidence
→ Legal provision или internal document version
→ Source snapshot.

Для юридической citation при наличии данных должны отображаться:
- название;
- номер;
- дата;
- редакция;
- статья;
- пункт/часть/подпункт;
- source;
- locator.

Нельзя создавать citation на основании предположения модели.

## 25. Claim validation

После генерации ответа выполняется проверка существенных утверждений.

Для claim должно быть найдено подтверждающее evidence.

Если claim не подтверждается:
- удалить;
- изменить формулировку;
- перевести ответ в недостаточно подтвержденный;
- эскалировать.

LLM не сама назначает citation как достоверную.

## 26. Статусы ответа

Минимальный enum:
- SUPPORTED
- PARTIALLY_SUPPORTED
- INSUFFICIENT_EVIDENCE
- CONFLICTING_SOURCES
- AMBIGUOUS_VERSION
- OUTDATED_SOURCE
- ESCALATION_REQUIRED

UI отображает эти статусы русскими понятными формулировками.

Главное:
НЕ ПОДТВЕРЖДЕНО является системным состоянием, а не только фразой в prompt.

## 27. LLM Gateway

Обязательный слой:

Agent
→ LLM Gateway
→ Provider Adapter
→ Model.

Агентная логика не зависит от OpenAI/Anthropic/другого provider.

Можно менять:
- provider;
- model;
- generation settings;
- embedding provider/model;
- optional reranker.

## 28. Local LLM

Архитектура допускает local provider без изменения agent logic.

Существующая интеграция Ollama в cairnsearch является потенциальным донором.

Полноценный local inference не должен быть обязательным для архитектуры, но интерфейс должен существовать.

## 29. External LLM and privacy

Не отправлять во внешний LLM весь документ без необходимости.

Правильный путь:
полный документ
→ local/authorized retrieval
→ минимально необходимый evidence
→ LLM.

Но внешний provider все равно является внешней обработкой для переданного контекста.

Для конкретного provider требуется отдельный privacy/security review.

## 30. Authentication

Первая реализация:
локальные учетные записи + server-side session.

Пароли:
- никогда не хранить plaintext;
- использовать современный адаптивный password hash;
- параметрами hashing управлять конфигурацией.

OWASP рекомендует Argon2id как предпочтительный современный вариант для password storage.

## 31. Sessions

Использовать server-side sessions и безопасные cookie properties.

Требования:
- cryptographically random session id;
- server-side session state;
- expiration;
- logout;
- rotation при изменении привилегий;
- HttpOnly;
- Secure при HTTPS;
- SameSite.

## 32. Roles

Начальные роли:
- ADMIN
- LEGAL
- HR
- OCCUPATIONAL_SAFETY
- EMPLOYEE

Роль задает базовые permissions.

Она не дает автоматически доступ ко всем документам.

## 33. Document ACL

Effective permission = user + organization + role + document ACL.

Default deny.

Authorization должна выполняться в application layer и, где возможно, дополнительно в DB layer.

## 34. LLM is not authorization

Никогда:
LLM decides whether user may read document.

Только:
application authorization
→ authorized evidence
→ LLM.

## 35. Prompt injection

Непроверенный текст:
- user input;
- internal document content;
- external content;
- retrieved text

расценивается как data, а не instructions.

Не смешивать:
SYSTEM POLICY
USER REQUEST
UNTRUSTED DOCUMENT CONTENT
RETRIEVED EVIDENCE.

OWASP отмечает indirect prompt injection через внешние источники, включая файлы, и прямо указывает, что RAG сам по себе проблему не устраняет. Рекомендуются разделение данных и инструкций, least privilege, ограничение инструментов и human approval для привилегированных действий.

## 36. Tools

Каждый tool имеет:
- schema;
- authorization requirement;
- risk level;
- audit event.

LLM не получает прямого произвольного доступа к filesystem, database или secrets.

## 37. Юридический агент

Основные задачи:
- поиск применимых норм;
- анализ;
- сравнение редакций;
- анализ договоров;
- анализ внутренних документов;
- выявление рисков;
- drafting;
- citations;
- escalation.

Не разрешено:
- принимать окончательные юридические решения;
- подписывать;
- отправлять;
- менять legal history;
- придумывать нормы;
- придумывать судебную практику.

## 38. Кадровый агент

Основные задачи:
- прием;
- перевод;
- увольнение;
- трудовые договоры;
- приказы;
- отпуска;
- рабочее время;
- локальные документы;
- анализ по НПА;
- drafting.

Не разрешено:
- принимать решение вместо ответственного лица;
- обходить ACL;
- придумывать сроки и основания.

## 39. Агент охраны труда

Основные задачи:
- нормы ОТ;
- инструкции;
- обучение;
- инструктажи;
- локальные документы;
- чек-листы;
- проверка требований;
- drafting.

Не разрешено:
- автоматически признавать организацию соответствующей законодательству;
- придумывать обязательность документа;
- придумывать периодичность без источника.

## 40. Router

Router определяет:
- LEGAL;
- HR;
- OCCUPATIONAL_SAFETY;
- MULTI_DOMAIN.

Router не имеет права обходить access policies.

Multi-domain request может включать несколько областей, но orchestration остается контролируемой и ограниченной.

Не создавать свободную agent-to-agent цепочку без ограничений.

## 41. Memory

Разделить:
1. Conversation state.
2. Knowledge base.
3. Audit.

Не создавать бессрочную скрытую память, которая превращает старые ответы или сообщения сотрудников в факты права.

## 42. PII

PII detector является safety signal.

Он не заменяет:
- authorization;
- encryption;
- compliance controls.

Это особенно важно для кадровых документов.

## 43. File upload security

Обязательны:
- allowlist расширений;
- проверка реального типа;
- размерные лимиты;
- application-generated filename;
- authorization;
- quarantine;
- безопасное хранение;
- parser isolation;
- audit.

OWASP рекомендует не доверять только Content-Type, ограничивать типы и размер, а загрузку разрешать только авторизованным пользователям.

## 44. Parser isolation

Существующий subprocess isolation является хорошим донором.

Целевая isolation:
- memory limit;
- CPU timeout;
- no core dumps;
- stripped environment;
- no application secrets;
- forced termination;
- quarantine on failure.

## 45. API architecture

Группы:
- auth;
- users/admin;
- documents;
- legal;
- agents;
- search;
- audit;
- health.

Запрещены endpoints, которые позволяют пользователю передавать произвольный filesystem path для открытия файла.

Каждый endpoint:
request
→ auth
→ authorization
→ input validation
→ business operation
→ audit.

## 46. CORS / CSRF

CORS — allowlist based.

Для cookie sessions:
- CSRF protection;
- SameSite;
- appropriate origin checks.

## 47. Encryption

Разделить:
- transport encryption;
- storage encryption;
- backups;
- optional field/application encryption.

Key management зависит от deployment и требует отдельного deployment review.

## 48. Jobs

Фоновые jobs:
- ingestion;
- OCR;
- parsing;
- embeddings;
- reindex;
- backup;
- source refresh.

Jobs должны быть идемпотентными.

## 49. Idempotency

Повторная операция не должна:
- создавать duplicate legal versions;
- создавать duplicate provisions;
- создавать orphan embeddings;
- удалять существующие данные.

Используем deterministic identities and hashes.

## 50. Deduplication

Для internal documents:
- file hash;
- normalized content hash;
- chunk hash.

Для legal documents:
разные юридические редакции не считаются duplicate только из-за высокого сходства.

## 51. Delete semantics

Internal documents:
- revoke access;
- mark deleted;
- controlled physical deletion;
- remove retrieval dependencies;
- audit.

Legal history:
обычный пользователь не может физически удалить опубликованную историческую версию.

## 52. Backups

Backup должен охватывать:
- PostgreSQL;
- document storage;
- required configuration;
- key recovery strategy.

Backup считается надежным только после restore test.

## 53. Disaster recovery

Документировать:
- RPO;
- RTO;
- backup frequency;
- retention;
- restore procedure;
- key recovery.

Числа не придумывать до определения реальных требований.

## 54. Observability

Минимум:
- health;
- readiness/liveness;
- queue metrics;
- ingestion failures;
- retrieval latency;
- LLM latency;
- provider failures;
- cost/usage;
- DB health;
- storage health.

## 55. Cost tracking

Если provider предоставляет usage:
- provider;
- model;
- input tokens;
- output tokens;
- latency;
- estimated cost;
- provider request id.

Не предполагать одинаковую тарификацию между providers.

## 56. UI

Основные экраны:
- Login;
- Home;
- Agent chat;
- Documents;
- Legal Sources;
- Administration.

Ответ должен показывать:
- текст;
- статус;
- citations;
- evidence;
- warnings;
- escalation.

## 57. Стиль работы системы

При подтвержденном ответе:
ПОДТВЕРЖДЕНО.

При частично подтвержденном:
ЧАСТИЧНО ПОДТВЕРЖДЕНО.

При недостатке evidence:
НЕ ПОДТВЕРЖДЕНО.

Пользователь должен понимать, где факт подтвержден, а где данных недостаточно.

## 58. Пример legal query

Вопрос:
Какой срок действует для X на 1 марта 2026 года?

Поток:
- auth;
- role check;
- legal route;
- extract date;
- identify sources;
- retrieve;
- filter by effective period;
- resolve version;
- retrieve provision;
- generate candidate answer;
- validate claims;
- generate citations;
- final policy;
- audit.

Если версия не подтверждена:
НЕ ПОДТВЕРЖДЕНО.

## 59. Пример internal compliance query

Вопрос:
Соответствует ли наша инструкция действующим требованиям?

Поток:
internal document version
+
applicable legal versions
→ retrieval
→ requirement mapping
→ gap analysis
→ claims/citations
→ report.

Нельзя объявлять «соответствует законодательству» без определенного объема проверки и evidence chain.

## 60. Конфликт источников

Если два источника выглядят конфликтующими:
- сохранить обе позиции;
- проверить authority;
- проверить dates;
- проверить version;
- не выбирать случайно;
- escalate, если конфликт не разрешен.

## 61. User-supplied document

Пользовательский документ:
- не становится официальным правовым источником;
- имеет собственный source type;
- имеет provenance;
- может использоваться как evidence другого типа.

## 62. Юрисдикция

По умолчанию:
legal_system = BY.

Если вопрос о другой юрисдикции:
- не подменять иностранное право белорусским;
- не выдавать иностранный источник как BY source;
- явно указывать, что запрос находится вне поддерживаемой области, если отдельный foreign-law module не реализован.

## 63. Versioning

Versioning требуется для:
- legal data;
- internal documents;
- prompts/policies;
- model configuration;
- schema migrations;
- code.

Для audit сохраняется:
- кодовая версия;
- provider;
- model;
- policy version;
- evidence identifiers.

## 64. Prompt versioning

Каждый агент имеет версионированную policy.

Например:
legal_agent_policy v1.0
hr_agent_policy v1.0
ot_agent_policy v1.0.

При изменении policy создается новая версия.

## 65. Model versioning

Сохранять:
- provider;
- model;
- generation configuration, насколько доступно;
- embedding model;
- reranker;
- policy version.

## 66. Reproducibility

Нельзя обещать идентичный текст ответа LLM.

Можно и нужно обеспечить восстановимость:
- вопроса;
- evidence;
- legal version;
- citations;
- model metadata;
- policy version.

## 67. Retrieval evaluation

До заявления «retrieval готов» нужна тестовая база:
- реальные/разрешенные белорусские НПА;
- внутренние тестовые документы;
- вопросы;
- expected evidence;
- expected citation;
- date-dependent queries;
- no-answer queries;
- ambiguous queries.

## 68. Метрики

Минимум:
- Recall@k;
- Precision@k;
- MRR;
- NDCG;
- citation accuracy;
- unsupported-claim rate;
- abstention quality;
- retrieval latency;
- end-to-end latency;
- ingestion success rate.

Для юридического слоя особенно важны:
- correctness of citation;
- unsupported claim rate;
- correct abstention.

## 69. Security tests

Обязательны:
- unauthenticated access;
- broken access control / IDOR;
- role escalation;
- revoked ACL;
- path traversal;
- unsafe upload;
- prompt injection;
- session misuse;
- CSRF;
- secret leakage;
- cloud-provider leakage in local-only mode.

## 70. Negative acceptance tests

NEG-01: no auth → deny.
NEG-02: foreign document access → deny.
NEG-03: no evidence → NOT_CONFIRMED.
NEG-04: ambiguous versions → NOT_CONFIRMED / ambiguity status.
NEG-05: injected document instruction → remains untrusted content.
NEG-06: filesystem traversal → deny.
NEG-07: startup → no deletion.
NEG-08: invalid citation → reject output claim.
NEG-09: revoked access → excluded from retrieval.
NEG-10: prohibited legal action → deny/escalate.
NEG-11: cloud provider in local-only mode → provider not contacted.
NEG-12: source hash mismatch → source not published.
NEG-13: duplicate ingestion → no duplicate legal version.
NEG-14: internal document deletion → no orphan retrieval records.
NEG-15: role reduction → new authorization applies.

## 71. Migration from cairnsearch

Use as donors:
- extractors;
- OCR;
- hashing;
- quarantine;
- parser isolation;
- selected RAG interfaces.

Do not migrate as-is:
- SQLite production schema;
- current API authorization model;
- current document path behavior;
- current legal metadata assumptions;
- current hybrid retrieval;
- current citation layer;
- current startup lifecycle.

## 72. Final target topology

                    USER
                      ↓
                   WEB UI
                      ↓
                AUTH / SESSION
                      ↓
                RBAC / ACL
                      ↓
                AGENT ROUTER
          ┌───────────┼───────────┐
          ↓           ↓           ↓
        LEGAL        HR           OT
          └───────────┼───────────┘
                      ↓
                POLICY ENGINE
                      ↓
                 RETRIEVAL
                      ↓
                   EVIDENCE
                      ↓
                 LLM GATEWAY
                      ↓
              CLAIM VALIDATOR
                      ↓
               CITATION SERVICE
                      ↓
                FINAL POLICY
                      ↓
                    AUDIT

                    DATA PLANE
        ┌────────────┼────────────┐
        ↓            ↓            ↓
    PostgreSQL     pgvector   Object Storage
        │
    legal data
    users/ACL
    documents
    audit
    jobs

## 73. Final architectural decisions v1.0

Принято:
1. Modular monolith.
2. PostgreSQL primary database.
3. pgvector initial vector layer.
4. PostgreSQL lexical search.
5. Common Evidence model.
6. Legal knowledge separated from internal documents.
7. Immutable legal versions.
8. Effective periods.
9. Source snapshots.
10. Citation-first.
11. Claim validation.
12. Abstention.
13. Policy engine.
14. Authentication.
15. RBAC.
16. Document ACL.
17. Audit.
18. LLM Gateway.
19. Provider-independent agents.
20. Local LLM capability.
21. Private-first deployment.
22. No required public domain.
23. No autonomous legally significant actions.
24. No destructive startup.
25. No secrets in repository.

## 74. Решения, которые намеренно не фиксируются

Не фиксируем сейчас:
- конкретного LLM provider;
- конкретную модель;
- конкретный server provider;
- конкретный VPN;
- домен;
- cloud object storage provider;
- exact retrieval thresholds;
- exact RPO/RTO;
- автоматизацию конкретного legal source;
- окончательные legal compliance claims.

Каждое такое решение должно быть принято после проверки.

## 75. Следующая стадия разработки

После утверждения этой архитектуры создаются отдельные детальные specifications для:
1. database schema and migrations;
2. legal knowledge model;
3. document service and storage;
4. retrieval and citation;
5. auth/RBAC/ACL;
6. LLM Gateway;
7. agent specifications;
8. security model;
9. deployment;
10. test strategy.

Эти specifications должны соответствовать этой архитектуре и не противоречить ей.

## 76. Критерий готовности

Система не считается готовой только потому, что:
- открывается UI;
- отвечает модель;
- есть чат;
- есть кнопки трех агентов.

Минимальный доказуемый критерий:
- authentication реально работает;
- authorization реально работает;
- ACL реально влияет на retrieval;
- legal version resolution реально работает;
- provenance реально хранится;
- citation действительно ведет к evidence;
- unsupported claims блокируются/маркируются;
- prompt injection не получает привилегий;
- startup не удаляет данные;
- audit существует;
- backup/restore проверены;
- security tests проходят;
- retrieval evaluation измерена.

## 77. Основное правило

Лучше система, которая честно говорит «НЕ ПОДТВЕРЖДЕНО», чем система, которая уверенно придумывает норму законодательства Республики Беларусь.

Изменение архитектурного решения оформляется через ADR и проверку влияния на:
- безопасность;
- данные;
- retrieval;
- citations;
- агентов;
- deployment.
