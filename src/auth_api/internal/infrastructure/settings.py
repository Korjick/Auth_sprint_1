from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field('auth', validation_alias='PROJECT_NAME')

    # Настройка JWT
    jwt_secret_key: str = Field(validation_alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field('HS256', validation_alias='JWT_ALGORITHM')
    jwt_access_token_expire_minutes: int = Field(
        30, validation_alias='JWT_ACCESS_TOKEN_EXPIRE_MINUTES'
    )
    jwt_refresh_token_expire_days: int = Field(
        2, validation_alias='JWT_REFRESH_TOKEN_EXPIRE_DAYS'
    )

    # Настройки Postgres
    echo_sql: bool = Field(False, validation_alias='ECHO_SQL')
    postgres_host: str = Field('127.0.0.1', validation_alias='POSTGRES_HOST')
    postgres_port: int = Field(5432, validation_alias='POSTGRES_PORT')
    postgres_db: str = Field('auth', validation_alias='POSTGRES_DB')
    postgres_user: str = Field('postgres', validation_alias='POSTGRES_USER')
    postgres_password: str = Field('', validation_alias='POSTGRES_PASSWORD')

    # Настройки Redis
    redis_host: str = Field('127.0.0.1', validation_alias='REDIS_HOST')
    redis_port: int = Field(6379, validation_alias='REDIS_PORT')
    redis_db: int = Field(0, validation_alias='REDIS_DB')

    # Настройки gRPC сервера
    grpc_host: str = Field('0.0.0.0', validation_alias='GRPC_HOST')
    grpc_port: int = Field(50051, validation_alias='GRPC_PORT')

    # Настройка формата логов
    log_json: bool = Field(True, validation_alias='LOG_JSON')
    log_level: str = Field('INFO', validation_alias='LOG_LEVEL')

    # Настройки OpenTelemetry (traces)
    otel_enabled: bool = Field(False, validation_alias='OTEL_ENABLED')
    otel_service_name: str = Field('auth-api', validation_alias='OTEL_SERVICE_NAME')
    otel_service_version: str = Field(
        '0.1.0',
        validation_alias='OTEL_SERVICE_VERSION',
    )
    otel_environment: str = Field('development', validation_alias='OTEL_ENVIRONMENT')
    otel_exporter_otlp_endpoint: str = Field(
        'http://127.0.0.1:4317',
        validation_alias='OTEL_EXPORTER_OTLP_ENDPOINT',
    )
    otel_exporter_otlp_insecure: bool = Field(
        True,
        validation_alias='OTEL_EXPORTER_OTLP_INSECURE',
    )

    @classmethod
    def from_env(cls, env_file: str | None = None) -> 'Settings':
        if not env_file:
            return cls()

        env_path = Path(env_file)
        if not env_path.exists():
            raise FileNotFoundError(f"File {env_file} not found")

        if not env_path.is_file():
            raise ValueError(f"{env_file} is not a file")

        return cls(
            _env_file=str(env_path),
            _env_file_encoding='utf-8-sig'
        )
