# CODEX HANDOFF — I0/I1

Статус: implementation handoff
Target branch: `architecture/target-v1`
Base architecture: v1.1

## Purpose

Этот документ — точное задание для coding agent (Codex) на первый рабочий этап.

Codex должен НЕ переделывать архитектуру и НЕ строить чат. Его задача — реализовать только I0 + I1 из `docs/IMPLEMENTATION_PLAN.md`, опираясь на утвержденный baseline.

## Source of truth

Читай в таком порядке:

1. `docs/TARGET_ARCHITECTURE.md`
2. `docs/BUILD_SPECIFICATION.md`
3. `docs/IMPLEMENTATION_PLAN.md`
4. `docs/DATA_MODEL.md`
5. `docs/SECURITY_MODEL.md`
6. `docs/ADR.md`
7. `docs/ARCHITECTURE_REVIEW.md`

Существующий `cairnsearch` — только технический донор. Его архитектура НЕ является source of truth.

## Non-negotiable constraints

- Не менять `main`.
- Работать только в отдельной implementation-ветке, созданной от `architecture/target-v1`.
- Не удалять исторический код до понимания его зависимостей.
- Не переносить SQLite/FTS5 как целевое persistence-решение.
- Не сохранять destructive startup.
- Не создавать open-path endpoints.
- Не добавлять cloud LLM по умолчанию.
- Не вносить секреты в код, config examples, tests или Git.
- Не добавлять пользовательские/company data в репозиторий.
- Не строить UI/chat на этом этапе.
- Не вводить микросервисы.
- Не придумывать новые API/таблицы/permissions, если они не требуются архитектурой.
- При неоднозначности сначала остановиться и зафиксировать вопрос в отчете, а не угадывать.
- Любое архитектурное отклонение должно быть явно указано в completion report.

## Milestone I0 — Repository baseline and safety

### Цель

Создать безопасный фундамент проекта, на котором дальше можно без переделки реализовать PostgreSQL backend.

### Обязательно

1. Полностью проинспектировать текущую структуру приложения и точки запуска.
2. Найти все startup hooks, которые могут изменять или удалять данные.
3. Устранить/заблокировать destructive startup для target implementation.
4. Зафиксировать четкие package boundaries по bounded contexts, перечисленным в BUILD_SPECIFICATION.
5. Выбрать и подключить migration framework, совместимый с выбранным Python stack.
6. Настроить единый test runner.
7. Настроить lint/type-check только в объеме, который реально можно запускать локально.
8. Обеспечить безопасную конфигурацию через environment/config без секретов в repo.
9. Добавить базовый smoke test запуска приложения.
10. Добавить regression test, доказывающий, что startup не удаляет существующие данные.

### I0 acceptance

- Запуск приложения не удаляет данные.
- Тест destructive-startup проходит.
- Тестовый runner запускается одной командой.
- Migration command запускается одной командой.
- Архитектурные документы остаются доступными.
- Новая target implementation не зависит от старой SQLite schema как от persistence contract.
- Нет секретов и локальных data artifacts в Git.

## Milestone I1 — PostgreSQL foundation

### Цель

Создать PostgreSQL persistence foundation без реализации полноценного бизнес-функционала.

### Обязательно

1. PostgreSQL connection/config layer.
2. Transaction/session management.
3. Migration baseline.
4. UUID-based domain identifiers.
5. Базовые organization-independent инфраструктурные таблицы/структуры только там, где это прямо необходимо foundation layer.
6. Audit table foundation согласно архитектуре.
7. Подготовка optional pgvector extension без жесткой зависимости, если конкретное окружение его не поддерживает.
8. Health check для DB connectivity.
9. Integration tests на disposable/test PostgreSQL.
10. Проверка restart persistence: после перезапуска приложения данные в PostgreSQL сохраняются.
11. Повторный запуск migrations не разрушает данные.
12. Некорректная migration не должна silently drop/reset database.

### I1 acceptance

- Чистая установка: migrations применяются с нуля.
- Повторное применение: migrations idempotently recognized as already applied.
- Перезапуск PostgreSQL/application не удаляет данные.
- DB health check корректно отражает доступность БД.
- Integration tests проходят на реальном PostgreSQL, а не на SQLite substitute.
- Нет скрытой зависимости от локального пути пользователя.
- Нет SQL/DB access из Agent modules.

## Explicitly out of scope

На I0/I1 НЕ реализовывать:

- полноценный login UI;
- users/roles/permissions workflows;
- document upload;
- legal source ingestion;
- OCR;
- vector indexing;
- RAG;
- citation generation;
- LLM providers;
- LegalAgent/HRAgent/OccupationalSafetyAgent;
- router;
- chat UI.

Исключение: можно создать пустые интерфейсы/модули-заготовки только тогда, когда это нужно для package boundary и dependency direction. Они не должны притворяться работающей функциональностью.

## Safe reuse of old cairnsearch

Разрешено переиспользовать код только после проверки:

- security implications;
- dependency direction;
- persistence assumptions;
- path handling;
- subprocess/network behavior.

Особенно НЕ переносить без отдельного решения:

- `clear_all_data()`;
- arbitrary file-path access;
- старую SQLite schema;
- старый public/open API behavior;
- vendor-specific agent coupling.

## Expected repository result

После выполнения должен появиться:

- clean target package structure;
- migration setup;
- PostgreSQL infrastructure;
- test infrastructure;
- startup safety regression tests;
- DB integration tests;
- updated developer documentation for local execution.

Не требуется production deployment и не требуется public domain.

## Completion report — обязательный формат

В конце Codex должен вывести:

### Changed
Какие файлы созданы/изменены.

### Tests run
Точные команды и результат.

### Not run
Что не запускалось и почему.

### Architecture deviations
Только реальные отклонения. Если нет — `None`.

### Security findings
Найденные проблемы, даже если они остались вне scope.

### Known limitations
Что сознательно не реализовано.

### Unverified assumptions
Любые вещи, которые не удалось подтвердить.

### Acceptance matrix
Для каждого I0/I1 acceptance criterion:
`PASS / FAIL / BLOCKED` + evidence.

## Git discipline

- Делать небольшие reviewable commits.
- Не пушить в `main`.
- Не делать force-push.
- Не переписывать историю.
- После каждого значимого шага запускать относящиеся тесты.
- В commit message ясно указывать milestone, например:
  `I0 establish safe baseline`
  `I1 add PostgreSQL foundation`

---

# COPY-PASTE PROMPT FOR CODEX

Ты работаешь как senior backend/security engineer в существующем репозитории.

Сначала ПРОЧИТАЙ и используй как source of truth:

- docs/TARGET_ARCHITECTURE.md
- docs/BUILD_SPECIFICATION.md
- docs/IMPLEMENTATION_PLAN.md
- docs/DATA_MODEL.md
- docs/SECURITY_MODEL.md
- docs/ADR.md
- docs/ARCHITECTURE_REVIEW.md
- docs/CURSOR_HANDOFF_I0_I1.md

После чтения НЕ начинай сразу писать код.

Сначала:
1. проинспектируй текущий repository;
2. составь краткую карту текущей структуры;
3. найди startup paths;
4. найди destructive operations;
5. найди места, где старый SQLite является persistence assumption;
6. найди существующие test/config/migration mechanisms;
7. определи минимальный безопасный набор изменений для I0/I1.

Затем реализуй ТОЛЬКО I0 и I1.

Критические правила:

- не менять main;
- не строить chat/UI/agents;
- не переносить старую SQLite архитектуру;
- не сохранять destructive startup;
- не принимать arbitrary filesystem paths;
- не добавлять секреты;
- не придумывать отсутствующие контракты;
- не заявлять, что что-либо работает, пока это не запущено и не проверено;
- при конфликте кодовой базы и архитектурных документов приоритет имеют архитектурные документы;
- если архитектурный документ действительно неоднозначен и решение нельзя безопасно вывести из него, НЕ угадывай: остановись, зафиксируй BLOCKED item.

I0:
- safe startup;
- package boundaries;
- migration framework;
- test runner;
- smoke test;
- destructive-startup regression test;
- safe config foundation.

I1:
- PostgreSQL;
- migrations;
- transaction/session management;
- UUID identifiers;
- audit foundation;
- optional pgvector preparation;
- DB health check;
- real PostgreSQL integration tests;
- persistence across restart;
- migration safety.

Не делай mock-only substitute вместо настоящего PostgreSQL integration test.

После изменений:
1. запусти все относящиеся тесты;
2. запусти lint/type checks, если они настроены;
3. проверь repository на secrets и local data artifacts;
4. проверь, что startup больше не удаляет данные;
5. проверь, что повторные migrations безопасны;
6. проверь git diff на случайные широкие изменения.

В конце дай обязательный отчёт в формате:

Changed
Tests run
Not run
Architecture deviations
Security findings
Known limitations
Unverified assumptions
Acceptance matrix

В Acceptance matrix используй только PASS / FAIL / BLOCKED.

Не пиши "production ready".
Не изменяй архитектуру без явного documented deviation.
