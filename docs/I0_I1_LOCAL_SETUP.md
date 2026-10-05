# Локальный запуск target I0/I1

Этот документ относится только к новой target-реализации v1.1.
Старый SQLite/RAG workflow из `WINDOWS_INSTALL.md` не является инструкцией для I0/I1.

## 1. Переменная PostgreSQL

Нужно задать:

`CAIRNSEARCH_DATABASE_URL`

Пример формата:

`postgresql://USER:PASSWORD@HOST:5432/DATABASE`

Секрет не записывать в Git и не помещать в config example.

## 2. Установка

Создать виртуальное окружение и установить проект:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## 3. Миграции

Проверка текущего состояния:

```powershell
alembic current
```

Применение миграций:

```powershell
alembic upgrade head
```

Повторный запуск `alembic upgrade head` не должен повторно выполнять уже применённую миграцию.

## 4. Тесты

Unit/target tests:

```powershell
pytest -m target
```

Real PostgreSQL integration tests:

```powershell
pytest -m integration
```

Integration tests должны выполняться только against disposable/test PostgreSQL.
SQLite substitute для этих тестов не используется.

## 5. Что должно быть подтверждено после I0/I1

- startup не удаляет существующие данные;
- PostgreSQL подключается;
- migration baseline применяется;
- повторное применение миграций безопасно;
- audit foundation создаётся;
- UUID работают;
- transaction rollback работает;
- данные сохраняются между отдельными соединениями;
- DB health check отражает доступность PostgreSQL.

## 6. Ограничения этапа

На I0/I1 намеренно не реализуются:

- login UI;
- RBAC/ACL workflows;
- загрузка документов;
- юридический ingestion;
- OCR;
- RAG;
- embeddings;
- citations;
- LLM providers;
- три агента;
- router;
- chat UI.

Не считать систему production-ready на основании прохождения только I0/I1.
