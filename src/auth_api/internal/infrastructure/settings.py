from pathlib import Path

from pydantic import AliasChoices, Field
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
    otel_service_name: str = Field('auth-api',
                                   validation_alias='OTEL_SERVICE_NAME')
    otel_service_version: str = Field(
        '0.1.0',
        validation_alias='OTEL_SERVICE_VERSION',
    )
    otel_environment: str = Field('development',
                                  validation_alias='OTEL_ENVIRONMENT')
    otel_exporter_otlp_endpoint: str = Field(
        'http://127.0.0.1:4317',
        validation_alias='OTEL_EXPORTER_OTLP_ENDPOINT',
    )
    otel_exporter_otlp_insecure: bool = Field(
        True,
        validation_alias='OTEL_EXPORTER_OTLP_INSECURE',
    )

    # Настройки rate limit
    rate_limit_enabled: bool = Field(
        True,
        validation_alias='RATE_LIMIT_ENABLED'
    )
    rate_limit_fail_open: bool = Field(
        True,
        validation_alias='RATE_LIMIT_FAIL_OPEN'
    )
    rate_limit_api_ip_limit: int = Field(
        300,
        validation_alias='RATE_LIMIT_API_IP_LIMIT',
    )
    rate_limit_api_ip_window_sec: int = Field(
        60,
        validation_alias='RATE_LIMIT_API_IP_WINDOW_SEC',
    )
    rate_limit_signup_ip_limit: int = Field(
        10,
        validation_alias='RATE_LIMIT_SIGNUP_IP_LIMIT',
    )
    rate_limit_signup_ip_window_sec: int = Field(
        60,
        validation_alias='RATE_LIMIT_SIGNUP_IP_WINDOW_SEC',
    )
    rate_limit_login_ip_limit: int = Field(
        30,
        validation_alias='RATE_LIMIT_LOGIN_IP_LIMIT',
    )
    rate_limit_login_ip_window_sec: int = Field(
        60,
        validation_alias='RATE_LIMIT_LOGIN_IP_WINDOW_SEC',
    )
    rate_limit_login_key_ip_limit: int = Field(
        5,
        validation_alias='RATE_LIMIT_LOGIN_KEY_IP_LIMIT',
    )
    rate_limit_login_key_ip_window_sec: int = Field(
        60,
        validation_alias='RATE_LIMIT_LOGIN_KEY_IP_WINDOW_SEC',
    )
    rate_limit_refresh_user_limit: int = Field(
        30,
        validation_alias='RATE_LIMIT_REFRESH_USER_LIMIT',
    )
    rate_limit_refresh_user_window_sec: int = Field(
        60,
        validation_alias='RATE_LIMIT_REFRESH_USER_WINDOW_SEC',
    )

    # Настройки Google OAuth
    oauth_state_ttl_sec: int = Field(
        300,
        validation_alias="OAUTH_STATE_TTL_SEC",
    )
    oauth_google_enabled: bool = Field(
        False,
        validation_alias="OAUTH_GOOGLE_ENABLED",
    )
    oauth_google_client_id: str = Field(
        "",
        validation_alias="OAUTH_GOOGLE_CLIENT_ID",
    )
    oauth_google_client_secret: str = Field(
        "",
        validation_alias="OAUTH_GOOGLE_CLIENT_SECRET",
    )
    oauth_google_redirect_uri: str = Field(
        "",
        validation_alias="OAUTH_GOOGLE_REDIRECT_URI",
    )
    oauth_google_authorize_url: str = Field(
        "https://accounts.google.com/o/oauth2/v2/auth",
        validation_alias="OAUTH_GOOGLE_AUTHORIZE_URL",
    )
    oauth_google_token_url: str = Field(
        "https://oauth2.googleapis.com/token",
        validation_alias="OAUTH_GOOGLE_TOKEN_URL",
    )
    oauth_google_jwks_url: str = Field(
        "https://www.googleapis.com/oauth2/v3/certs",
        validation_alias="OAUTH_GOOGLE_JWKS_URL",
    )
    oauth_google_scopes: str = Field(
        "openid email profile",
        validation_alias="OAUTH_GOOGLE_SCOPES",
    )
    oauth_google_issuer_primary: str = Field(
        "https://accounts.google.com",
        validation_alias="OAUTH_GOOGLE_ISSUER_PRIMARY",
    )
    oauth_google_issuer_secondary: str = Field(
        "accounts.google.com",
        validation_alias="OAUTH_GOOGLE_ISSUER_SECONDARY",
    )
    oauth_google_http_timeout_sec: float = Field(
        5.0,
        validation_alias="OAUTH_GOOGLE_HTTP_TIMEOUT_SEC",
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
