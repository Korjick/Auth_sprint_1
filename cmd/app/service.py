import asyncio
import logging
from contextlib import asynccontextmanager

import typer
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from internal.adapters.input.http import base_exception_handlers
from internal.adapters.input.http.v1.user import routes as user_routes
from internal.adapters.input.http.v1.role import routes as role_routes
from internal.adapters.output.redis.cache_provider import RedisCacheProvider
from internal.infrastructure.jwt import PyJWTTokenProvider
from internal.infrastructure.password import WerkzeugHashProvider
from internal.infrastructure.settings import Settings
from internal.infrastructure.time_provider import UtcTimeProvider
from internal.infrastructure.uow import SqlAlchemyUnitOfWork

service_cli = typer.Typer(
    name='auth',
    help='Authentication API service',
    add_completion=False,
)


def _create_app(env_file: str = ".env") -> FastAPI:
    settings = Settings.from_env(env_file)

    dsn = (f'postgresql+asyncpg://{settings.postgres_user}:'
           f'{settings.postgres_password}'
           f'@{settings.postgres_host}:{settings.postgres_port}'
           f'/{settings.postgres_db}')
    db_engine = create_async_engine(dsn, echo=settings.echo_sql, future=True)
    db_session_factory = async_sessionmaker(db_engine, expire_on_commit=False)

    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logging.info("Application started")
        yield
        await db_engine.dispose()
        await redis_client.close()
        logging.info("Application shutdown")

    app = FastAPI(
        title=settings.project_name,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        description="Authentication API service",
    )

    app.state.cache_provider = RedisCacheProvider(redis_client,
                                                  settings.project_name)
    app.state.time_provider = UtcTimeProvider()
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
    app.include_router(user_routes.router, prefix="/api/v1")
    app.include_router(role_routes.router, prefix="/api/v1")

    return app


async def _create_superuser_async(app: FastAPI, login: str,
                                  password: str) -> None:
    from internal.ports.output.user_repository import UserCreate
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


app: FastAPI = _create_app()


@service_cli.command()
def run(env_file: str = typer.Option('.env',
                                     "--env-file", "-e",
                                     help="Path to the .env file"),
        host: str = typer.Option("0.0.0.0",
                                 "--host", "-h",
                                 help="Host of server"),
        port: int = typer.Option(8080,
                                 "--port", "-p",
                                 help="Port of server"),
        reload: bool = typer.Option(False,
                                    "--reload",
                                    help="Autoreload then file changing")) \
        -> None:
    global app
    app = _create_app(env_file)
    uvicorn.run("cmd.app.service:app", host=host, port=port, reload=reload)


@service_cli.command()
def create_superuser(
        env_file: str = typer.Option('.env',
                                     "--env-file", "-e",
                                     help="Path to the .env file"),
        login: str = typer.Option("superuser",
                                  '--login', '-l',
                                  help="User login"),
        password: str = typer.Option("", '--password', '-p',
                                     help="User password")) -> None:
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
