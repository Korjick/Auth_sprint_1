import asyncio
import os
from contextlib import asynccontextmanager

import grpc
import typer
import uvicorn
from Auth_sprint_2.v1 import auth_pb2_grpc
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from auth_api.internal.adapters.input.grpc.auth.v1.auth_service import AuthGrpcService
from auth_api.internal.adapters.input.http import base_exception_handlers
from auth_api.internal.adapters.input.http.dependencies import api_rate_limit
from auth_api.internal.adapters.input.http.middlewares.request_middleware import (
    RequestContextMiddleware,
)
from auth_api.internal.adapters.input.http.v1.role import routes as role_routes
from auth_api.internal.adapters.input.http.v1.user import routes as user_routes
from auth_api.internal.adapters.output.redis.cache_provider import RedisCacheProvider
from auth_api.internal.infrastructure.jwt import PyJWTTokenProvider
from auth_api.internal.infrastructure.logger import StructlogLogger
from auth_api.internal.infrastructure.password import WerkzeugHashProvider
from auth_api.internal.infrastructure.rate_limiter import (
    RedisFixedWindowRateLimiter,
)
from auth_api.internal.infrastructure.settings import Settings
from auth_api.internal.infrastructure.telemetry import (
    setup_telemetry,
    shutdown_telemetry,
)
from auth_api.internal.infrastructure.time_provider import UtcTimeProvider
from auth_api.internal.infrastructure.uow import SqlAlchemyUnitOfWork
from auth_api.internal.ports.output.logger import Logger
from auth_api.internal.ports.output.rate_limiter import (
    FixedWindowLimit,
    RateLimitConfig,
)

service_cli = typer.Typer(
    name="auth",
    help="Authentication API service",
    add_completion=False,
)


def _create_app(env_file: str | None = None) -> FastAPI:
    settings = Settings.from_env(env_file)
    rate_limit_config = RateLimitConfig(
        enabled=settings.rate_limit_enabled,
        api_ip=FixedWindowLimit(
            limit=settings.rate_limit_api_ip_limit,
            window_sec=settings.rate_limit_api_ip_window_sec,
        ),
        signup_ip=FixedWindowLimit(
            limit=settings.rate_limit_signup_ip_limit,
            window_sec=settings.rate_limit_signup_ip_window_sec,
        ),
        login_ip=FixedWindowLimit(
            limit=settings.rate_limit_login_ip_limit,
            window_sec=settings.rate_limit_login_ip_window_sec,
        ),
        login_key_ip=FixedWindowLimit(
            limit=settings.rate_limit_login_key_ip_limit,
            window_sec=settings.rate_limit_login_key_ip_window_sec,
        ),
        refresh_user=FixedWindowLimit(
            limit=settings.rate_limit_refresh_user_limit,
            window_sec=settings.rate_limit_refresh_user_window_sec,
        ),
    )
    StructlogLogger.configure(
        json_logs=settings.log_json,
        log_level=settings.log_level,
    )
    app_logger: Logger = StructlogLogger.from_name(__name__)

    dsn = (
        f"postgresql+asyncpg://{settings.postgres_user}:"
        f"{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}"
        f"/{settings.postgres_db}"
    )
    db_engine = create_async_engine(dsn, echo=settings.echo_sql, future=True)
    db_session_factory = async_sessionmaker(db_engine, expire_on_commit=False)

    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app_logger.info("application_started")
        grpc_server = grpc.aio.server()
        auth_pb2_grpc.add_AuthServiceServicer_to_server(
            AuthGrpcService(app.state.token_provider, app.state.logger),
            grpc_server,
        )
        grpc_bind = f"{settings.grpc_host}:{settings.grpc_port}"
        grpc_server.add_insecure_port(grpc_bind)
        await grpc_server.start()
        app_logger.info("grpc_server_started", grpc_bind=grpc_bind)
        try:
            yield
        finally:
            await grpc_server.stop(grace=3)
            await db_engine.dispose()
            await redis_client.close()
            shutdown_telemetry()
            app_logger.info("application_shutdown")

    app = FastAPI(
        title=settings.project_name,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        description="Authentication API service",
    )
    app.state.settings = settings
    app.state.logger = app_logger
    app.add_middleware(RequestContextMiddleware)
    setup_telemetry(app=app, settings=settings, db_engine=db_engine)
    app_logger.info(
        "telemetry_configured",
        otel_endpoint=settings.otel_exporter_otlp_endpoint,
        otel_service_name=settings.otel_service_name,
    )

    app.state.cache_provider = RedisCacheProvider(redis_client,
                                                  settings.project_name)
    time_provider = UtcTimeProvider()
    app.state.rate_limiter = RedisFixedWindowRateLimiter(
        redis_client=redis_client,
        project_name=settings.project_name,
        logger=app_logger.branch(component="rate_limiter"),
        config=rate_limit_config,
        time_provider=time_provider,
        fail_open=settings.rate_limit_fail_open,
    )
    app.state.time_provider = time_provider
    app.state.token_provider = PyJWTTokenProvider(
        settings.jwt_secret_key,
        settings.jwt_algorithm,
        settings.jwt_access_token_expire_minutes,
        settings.jwt_refresh_token_expire_days,
        app.state.time_provider,
        app.state.cache_provider,
    )
    app.state.hash_provider = WerkzeugHashProvider()
    app.state.uow = SqlAlchemyUnitOfWork(db_session_factory)

    base_exception_handlers.setup_exception_handlers(app)
    app.include_router(
        user_routes.router,
        prefix="/api/v1",
        dependencies=[Depends(api_rate_limit)],
    )
    app.include_router(
        role_routes.router,
        prefix="/api/v1",
        dependencies=[Depends(api_rate_limit)],
    )

    return app


async def _create_superuser_async(app: FastAPI, login: str,
                                  password: str) -> None:
    from auth_api.internal.ports.output.user_repository import UserCreate

    uow = app.state.uow
    hash_provider = app.state.hash_provider
    hashed = hash_provider.hash_data(password)
    user_to_create = UserCreate(
        login=login,
        password_hash=hashed,
        first_name="Super",
        last_name="User",
        is_superuser=True,
        is_active=True,
    )
    async with uow:
        await uow.users.save_user(user_to_create)
        await uow.commit()
    typer.echo(f"Superuser {login!r} created.")


def create_app() -> FastAPI:
    env_file = os.getenv("AUTH_ENV_FILE")
    return _create_app(env_file)


@service_cli.command()
def run(
        env_file: str | None = typer.Option(
            None,
            "--env-file",
            "-e",
            help="Path to the .env file",
        ),
        host: str = typer.Option("0.0.0.0", "--host", "-h",
                                 help="Host of server"),
        port: int = typer.Option(8080, "--port", "-p",
                                 help="Port of server"),
        reload: bool = typer.Option(False, "--reload",
                                    help="Autoreload then file changing"),
) -> None:
    if env_file:
        os.environ["AUTH_ENV_FILE"] = env_file
    else:
        os.environ.pop("AUTH_ENV_FILE", None)
    uvicorn.run(
        "auth_api.cmd.app.service:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
    )


@service_cli.command()
def create_superuser(
        env_file: str | None = typer.Option(
            None,
            "--env-file",
            "-e",
            help="Path to the .env file",
        ),
        login: str = typer.Option("superuser",
                                  "--login", "-l",
                                  help="User login"),
        password: str = typer.Option("", "--password", "-p",
                                     help="User password"),
) -> None:
    try:
        Settings.from_env(env_file)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    app = _create_app(env_file)
    if not password:
        password = typer.prompt("Password", hide_input=True)
    try:
        asyncio.run(_create_superuser_async(app, login, password))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    service_cli()

