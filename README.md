# Auth Service

https://github.com/Korjick/Auth_sprint_1

Сервис аутентификации и авторизации для онлайн-кинотеатра. Реализует
регистрацию, аутентификацию по JWT, управление сессиями и систему ролей.

## Стек

- Python 3.13, FastAPI, SQLAlchemy (async), Alembic
- PostgreSQL — хранение пользователей, ролей, сессий
- Redis — блэклист токенов
- PyJWT, Werkzeug — JWT и хеширование паролей
- OpenTelemetry + Jaeger — распределённые трейсы
- Typer — CLI

## Архитектура

Hexagonal (Ports & Adapters). Слои:

```
src/auth_api/internal/
  core/domain/models/    — доменные модели (User, Role, Session)
  core/application/      — use cases (commands, queries)
  ports/input/           — протоколы входных портов (handler interfaces)
  ports/output/          — протоколы выходных портов (repository, provider interfaces)
  adapters/input/http/   — FastAPI-роутеры
  adapters/output/       — реализации репозиториев (Postgres, Redis)
  infrastructure/        — JWT, password hashing, UoW, settings
src/auth_api/cmd/app/    — точка входа (CLI)
```

## Запуск

### 1. Настройка окружения

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

pip install -r requirements.txt
pip install -e .
```

### 2. Конфигурация

Для локальной разработки используется `.env.sample`.
Для production-подобного запуска используйте `.env`.

### 3. Запуск инфраструктуры

Dev (локальная инфраструктура для запуска приложения с хоста: БД/Redis/Jaeger):

```bash
docker compose -f docker-compose.dev.yaml up -d
```

Prod (приложение в контейнере + миграции + БД/Redis + Loki/Promtail + Jaeger):

```bash
docker compose -f docker-compose.yaml up -d
```

Loki API: `http://localhost:3100`
Jaeger UI: `http://localhost:16686`

### 4. Применение миграций

```bash
python -m auth_api.cmd.app.main db upgrade --env-file .env.sample
```

### 5. Создание суперпользователя

```bash
python -m auth_api.cmd.app.main service create-superuser --env-file .env.sample --login admin --password <пароль>
```

### 6. Запуск сервера

```bash
python -m auth_api.cmd.app.main service run --env-file .env.sample --host 0.0.0.0 --port 8080
```

Swagger-документация: `http://localhost:8080/api/openapi`

## Трейсинг (OpenTelemetry + Jaeger)

В `.env.sample` добавлены параметры:

- `OTEL_ENABLED` — включить/выключить экспорт трейсов.
- `OTEL_SERVICE_NAME` — имя сервиса в Jaeger.
- `OTEL_SERVICE_VERSION` — версия сервиса.
- `OTEL_ENVIRONMENT` — окружение (`development`/`production`).
- `OTEL_EXPORTER_OTLP_ENDPOINT` — OTLP endpoint (`http://127.0.0.1:4317` для локального запуска с хоста).
- `OTEL_EXPORTER_OTLP_INSECURE` — отключение TLS для локального окружения.

Для контейнерного запуска `auth_api` endpoint автоматически переопределяется на `http://jaeger:4317` в `docker-compose.yaml`.

## CLI-команды

```
python -m auth_api.cmd.app.main [service, db] --help
```

Все команды принимают `--env-file` / `-e` для указания пути к `.env`.

## Тесты

### Установка зависимостей

```bash
pip install -r requirements-test.txt
```

### Unit-тесты

```bash
pytest tests/unit -v
```

### Интеграционные тесты (требуют Docker)

```bash
pytest tests/integration -v
```

Интеграционные тесты используют testcontainers — автоматически поднимают
PostgreSQL и Redis в Docker-контейнерах.

### Все тесты

```bash
pytest -v
```

## Авторы

- Булат — разработка 
