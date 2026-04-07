from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from redis.asyncio import Redis

from auth_api.internal.adapters.output.postgres.models import Base


@pytest.fixture(scope="session")
def postgres_container():
    """РџРѕРґРЅРёРјР°РµС‚ PostgreSQL РєРѕРЅС‚РµР№РЅРµСЂ РЅР° РІСЂРµРјСЏ С‚РµСЃС‚РѕРІРѕР№ СЃРµСЃСЃРёРё."""
    with PostgresContainer(
        image="postgres:16-alpine",
        username="test",
        password="test",
        dbname="test_auth",
    ) as pg:
        yield pg


@pytest.fixture(scope="session")
def redis_container():
    """РџРѕРґРЅРёРјР°РµС‚ Redis РєРѕРЅС‚РµР№РЅРµСЂ РЅР° РІСЂРµРјСЏ С‚РµСЃС‚РѕРІРѕР№ СЃРµСЃСЃРёРё."""
    with RedisContainer() as r:
        yield r


@pytest.fixture(scope="session")
def postgres_url(postgres_container) -> str:
    """Async DSN РґР»СЏ РїРѕРґРєР»СЋС‡РµРЅРёСЏ Рє С‚РµСЃС‚РѕРІРѕРјСѓ PostgreSQL."""
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    return (
        f"postgresql+asyncpg://test:test@{host}:{port}/test_auth"
    )


@pytest.fixture(scope="session")
def redis_url(redis_container) -> str:
    """URL РґР»СЏ РїРѕРґРєР»СЋС‡РµРЅРёСЏ Рє С‚РµСЃС‚РѕРІРѕРјСѓ Redis."""
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    return f"redis://{host}:{port}/0"


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_engine(postgres_url):
    """РЎРѕР·РґР°С‘С‚ async engine Рё РёРЅРёС†РёР°Р»РёР·РёСЂСѓРµС‚ СЃС…РµРјСѓ + С‚Р°Р±Р»РёС†С‹."""
    engine = create_async_engine(postgres_url, echo=False)

    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS service"))
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db_session_factory(async_engine) -> async_sessionmaker:
    """Р¤Р°Р±СЂРёРєР° СЃРµСЃСЃРёР№ SQLAlchemy."""
    return async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(db_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """РћРґРЅР° СЃРµСЃСЃРёСЏ Р‘Р” СЃ РѕС‚РєР°С‚РѕРј РїРѕСЃР»Рµ РєР°Р¶РґРѕРіРѕ С‚РµСЃС‚Р°."""
    async with db_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(loop_scope="session")
async def redis_client(redis_url) -> AsyncGenerator[Redis, None]:
    """Async Redis РєР»РёРµРЅС‚ вЂ” РЅРѕРІС‹Р№ РЅР° РєР°Р¶РґС‹Р№ С‚РµСЃС‚."""
    client = Redis.from_url(redis_url, decode_responses=True)
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()

