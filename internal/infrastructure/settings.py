from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field('auth', validation_alias='PROJECT_NAME')

    # Настройка JWT
    jwt_secret_key: str = Field('', validation_alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field('HS256', validation_alias='JWT_ALGORITHM')
    jwt_access_token_expire_minutes: int = Field(
        30, validation_alias='JWT_ACCESS_TOKEN_EXPIRE_MINUTES'
    )
    jwt_refresh_token_expire_days: int = Field(
        2, validation_alias='JWT_REFRESH_TOKEN_EXPIRE_DAYS'
    )

    # Настройки Postgres
    postgres_host: str = Field('127.0.0.1', validation_alias='POSTGRES_HOST')
    postgres_port: int = Field(5432, validation_alias='POSTGRES_PORT')
    postgres_db: str = Field('auth', validation_alias='POSTGRES_DB')
    postgres_user: str = Field('postgres', validation_alias='POSTGRES_USER')
    postgres_password: str = Field('', validation_alias='POSTGRES_PASSWORD')

    # Настройки Redis
    redis_host: str = Field('127.0.0.1', validation_alias='REDIS_HOST')
    redis_port: int = Field(6379, validation_alias='REDIS_PORT')
    redis_db: int = Field(0, validation_alias='REDIS_DB')

    @classmethod
    def from_env(cls, env_file: str) -> 'Settings':
        env_path = Path(env_file)
        if not env_path.exists():
            raise FileNotFoundError(f"File {env_file} not found")

        if not env_path.is_file():
            raise ValueError(f"{env_file} is not a file")

        return cls(
            _env_file=str(env_path),
            _env_file_encoding='utf-8'
        )
