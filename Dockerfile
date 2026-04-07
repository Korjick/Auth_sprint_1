FROM python:3.14-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

WORKDIR /app

RUN chown -R appuser:appuser /app

COPY requirements.txt pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir .

COPY alembic/ ./alembic/
COPY alembic.ini ./

USER appuser

EXPOSE 8080
CMD ["python", "-m", "auth_api.cmd.app.main", "service", "run", "--env-file", ".env", "--host", "0.0.0.0", "--port", "8080"]
