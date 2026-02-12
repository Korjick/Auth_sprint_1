# Auth Service 

https://github.com/Korjick/Auth_sprint_1

Сервис аутентификации и авторизации для онлайн-кинотеатра. Реализует регистрацию, аутентификацию по JWT, управление сессиями и систему ролей.

## Стек

- Python 3.13, FastAPI, SQLAlchemy (async), Alembic
- PostgreSQL — хранение пользователей, ролей, сессий
- Redis — блэклист токенов
- PyJWT, Werkzeug — JWT и хеширование паролей
- Typer — CLI

## Архитектура

Hexagonal (Ports & Adapters). Слои:

```
internal/
  core/domain/models/    — доменные модели (User, Role, Session)
  core/application/      — use cases (commands, queries)
  ports/input/           — протоколы входных портов (handler interfaces)
  ports/output/          — протоколы выходных портов (repository, provider interfaces)
  adapters/input/http/   — FastAPI-роутеры
  adapters/output/       — реализации репозиториев (Postgres, Redis)
  infrastructure/        — JWT, password hashing, UoW, settings
cmd/app/                 — точка входа (CLI)
```

## Запуск

### 1. Настройка окружения

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 2. Конфигурация

Создать файл `.env` в корне проекта:

```dotenv
PROJECT_NAME=auth

POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=auth
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<пароль>

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0

JWT_SECRET_KEY=<секретный_ключ_минимум_32_символа>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=2
```

### 3. Запуск инфраструктуры

```bash
docker compose -f docker-compose.dev.yaml up -d
```

### 4. Применение миграций

```bash
python -m cmd.app.main db upgrade --env-file .env
```

### 5. Создание суперпользователя

```bash
python -m cmd.app.main service create-superuser --login admin --password <пароль>
```

### 6. Запуск сервера

```bash
python -m cmd.app.main service run --env-file .env --host 0.0.0.0 --port 8080
```

Swagger-документация: `http://localhost:8080/api/openapi`

## CLI-команды

```
python -m cmd.app.main [service, db] --help
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

Интеграционные тесты используют testcontainers — автоматически поднимают PostgreSQL и Redis в Docker-контейнерах.

### Все тесты

```bash
pytest -v
```

## Авторы

- Булат — разработка 
