import datetime
import uuid
from collections.abc import Callable

import pytest

from auth_api.internal.core.domain.models.role.role import Role, ADMIN_ROLE_NAME
from auth_api.internal.core.domain.models.session.session import Session
from auth_api.internal.core.domain.models.user.user import User
from auth_api.internal.infrastructure.jwt import PyJWTTokenProvider
from auth_api.internal.ports.output.cache_provider import CacheProvider
from auth_api.internal.ports.output.token_provider import TokenProvider, UserTokenData
from tests.unit.fakes import FakeTimeProvider, FakeCacheProvider


@pytest.fixture
def token_provider_factory() -> Callable[..., TokenProvider]:
    def _factory(
            secret: str = "test-secret",
            algorithm: str = "HS256",
            access_minutes: int = 30,
            refresh_days: int = 2,
            fixed_time: datetime.datetime | None = None,
            cache: CacheProvider | None = None,
    ) -> TokenProvider:
        return PyJWTTokenProvider(
            secret_key=secret,
            algorithm=algorithm,
            access_token_timedelta_minutes=access_minutes,
            refresh_token_timedelta_days=refresh_days,
            time_provider=FakeTimeProvider(fixed_time),
            cache_provider=cache or FakeCacheProvider(),
        )

    return _factory


@pytest.fixture
def user_factory() -> Callable[..., User]:
    def _factory(**overrides) -> User:
        defaults = dict(
            oid=uuid.uuid4(),
            login="john_doe",
            password_hash="hashed_password_123",
            first_name="John",
            last_name="Doe",
            roles=["subscriber"],
            is_superuser=False,
            is_active=True,
            created_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
        )
        defaults.update(overrides)
        return User(**defaults)

    return _factory


@pytest.fixture
def role_factory() -> Callable[..., Role]:
    def _factory(**overrides) -> Role:
        defaults = dict(
            oid=uuid.uuid4(),
            name=ADMIN_ROLE_NAME,
        )
        defaults.update(overrides)
        return Role(**defaults)

    return _factory


@pytest.fixture
def session_factory() -> Callable[..., Session]:
    def _factory(**overrides) -> Session:
        defaults = dict(
            oid=uuid.uuid4(),
            user_id=uuid.uuid4(),
            jti=uuid.uuid4(),
            device_fingerprint="Mozilla/5.0|en-US|127.0.0.1",
            expire_at=datetime.datetime(2025, 6, 1, 12, 0, 0),
        )
        defaults.update(overrides)
        return Session(**defaults)

    return _factory


@pytest.fixture
def user_token_data_factory() -> Callable[..., UserTokenData]:
    def _factory(**overrides) -> UserTokenData:
        defaults = dict(
            user_id=uuid.uuid4(),
            roles=["subscriber"],
            is_superuser=False,
        )
        defaults.update(overrides)
        return UserTokenData(**defaults)

    return _factory

