import uuid
import datetime

import pytest

from internal.infrastructure.jwt import PyJWTTokenProvider
from internal.ports.output.token_provider import (
    CreateTokenData,
    UserTokenData,
)
from internal.pkg.errors import UnauthorizedError


class FakeCacheProvider:
    """In-memory заглушка для CacheProvider."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def cache_data(self, key: str, data: str | int | float,
                         expire_sec: int):
        self._store[key] = str(data)

    async def get_from_cache(self, key: str) -> str | None:
        return self._store.get(key)


class FakeTimeProvider:
    """Детерминированный TimeProvider для тестов."""

    def __init__(self, fixed_now: datetime.datetime | None = None):
        self._now = fixed_now or datetime.datetime.now(
            datetime.timezone.utc).replace(tzinfo=None)

    def now_utc(self) -> datetime.datetime:
        return self._now

    def from_timestamp(self, timestamp: int | float) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(timestamp).replace(tzinfo=None)


def _make_provider(
        secret: str = "test-secret",
        algorithm: str = "HS256",
        access_minutes: int = 30,
        refresh_days: int = 2,
        fixed_time: datetime.datetime | None = None,
        cache: FakeCacheProvider | None = None,
) -> PyJWTTokenProvider:
    return PyJWTTokenProvider(
        secret_key=secret,
        algorithm=algorithm,
        access_token_timedelta_minutes=access_minutes,
        refresh_token_timedelta_days=refresh_days,
        time_provider=FakeTimeProvider(fixed_time),
        cache_provider=cache or FakeCacheProvider(),
    )


def _make_user_token_data(**overrides) -> UserTokenData:
    defaults = dict(login="alice", roles=["subscriber"], is_superuser=False)
    defaults.update(overrides)
    return UserTokenData(**defaults)


class TestCreateToken:
    """Тесты создания токенов."""

    def test_create_access_token_returns_string(self):
        """create_token для access возвращает строку."""
        provider = _make_provider()
        token = provider.create_token(
            CreateTokenData(user=_make_user_token_data(), refresh=False)
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_returns_string(self):
        """create_token для refresh возвращает строку."""
        provider = _make_provider()
        token = provider.create_token(
            CreateTokenData(user=_make_user_token_data(), refresh=True)
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_and_refresh_tokens_differ(self):
        """Access и refresh токены различаются (разный jti)."""
        provider = _make_provider()
        user = _make_user_token_data()
        access = provider.create_token(
            CreateTokenData(user=user, refresh=False))
        refresh = provider.create_token(
            CreateTokenData(user=user, refresh=True))
        assert access != refresh


class TestDecodeToken:
    """Тесты декодирования токенов."""

    def test_decode_access_token(self):
        """Декодированный access-токен содержит корректные данные."""
        provider = _make_provider()
        user = _make_user_token_data(login="bob", roles=["admin"])
        token = provider.create_token(
            CreateTokenData(user=user, refresh=False)
        )

        decoded = provider.decode_token(token)
        assert decoded.user.login == "bob"
        assert decoded.user.roles == ["admin"]
        assert decoded.refresh is False
        assert isinstance(decoded.jti, uuid.UUID)
        assert isinstance(decoded.exp, datetime.datetime)

    def test_decode_refresh_token(self):
        """Декодированный refresh-токен имеет refresh=True."""
        provider = _make_provider()
        token = provider.create_token(
            CreateTokenData(user=_make_user_token_data(), refresh=True)
        )
        decoded = provider.decode_token(token)
        assert decoded.refresh is True

    def test_decode_preserves_superuser_flag(self):
        """Флаг is_superuser сохраняется в токене."""
        provider = _make_provider()
        user = _make_user_token_data(is_superuser=True)
        token = provider.create_token(
            CreateTokenData(user=user, refresh=False)
        )
        decoded = provider.decode_token(token)
        assert decoded.user.is_superuser is True

    def test_decode_invalid_token_raises_unauthorized(self):
        """Невалидный токен вызывает UnauthorizedError."""
        provider = _make_provider()
        with pytest.raises(UnauthorizedError):
            provider.decode_token("invalid.token.string")

    def test_decode_token_with_wrong_secret_raises_unauthorized(self):
        """Токен подписанный другим секретом вызывает UnauthorizedError."""
        provider1 = _make_provider(secret="secret-1")
        provider2 = _make_provider(secret="secret-2")

        token = provider1.create_token(
            CreateTokenData(user=_make_user_token_data(), refresh=False)
        )
        with pytest.raises(UnauthorizedError):
            provider2.decode_token(token)

    def test_expired_token_raises_unauthorized(self):
        """Истёкший токен вызывает UnauthorizedError."""
        past = datetime.datetime(2020, 1, 1)
        provider = _make_provider(fixed_time=past, access_minutes=1)
        token = provider.create_token(
            CreateTokenData(user=_make_user_token_data(), refresh=False)
        )
        # Токен создан в 2020 с TTL 1 минуту, уже истёк
        with pytest.raises(UnauthorizedError):
            provider.decode_token(token)


class TestBlacklist:
    """Тесты блэклиста токенов."""

    @pytest.mark.asyncio
    async def test_blacklist_and_check(self):
        """Заблокированный JTI определяется как blacklisted."""
        cache = FakeCacheProvider()
        provider = _make_provider(cache=cache)
        jti = uuid.uuid4()

        assert await provider.is_token_blacklisted(jti) is False

        await provider.blacklist_token(jti)
        assert await provider.is_token_blacklisted(jti) is True

    @pytest.mark.asyncio
    async def test_non_blacklisted_token(self):
        """Не заблокированный JTI не определяется как blacklisted."""
        cache = FakeCacheProvider()
        provider = _make_provider(cache=cache)

        assert await provider.is_token_blacklisted(uuid.uuid4()) is False
