import uuid
import datetime
from collections.abc import Callable

import pytest

from internal.ports.output.token_provider import (
    CreateTokenData,
    TokenProvider,
    UserTokenData,
)
from internal.pkg.errors import UnauthorizedError
from tests.unit.fakes import FakeCacheProvider


class TestCreateToken:
    """Тесты создания токенов."""

    def test_create_access_token_returns_string(
            self,
            token_provider_factory: Callable[..., TokenProvider],
            user_token_data_factory: Callable[..., UserTokenData],
    ):
        """create_token для access возвращает строку."""
        jwt_provider = token_provider_factory()
        token = jwt_provider.create_token(
            CreateTokenData(user=user_token_data_factory(), refresh=False)
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_returns_string(
            self,
            token_provider_factory: Callable[..., TokenProvider],
            user_token_data_factory: Callable[..., UserTokenData],
    ):
        """create_token для refresh возвращает строку."""
        jwt_provider = token_provider_factory()
        token = jwt_provider.create_token(
            CreateTokenData(user=user_token_data_factory(), refresh=True)
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_and_refresh_tokens_differ(
            self,
            token_provider_factory: Callable[..., TokenProvider],
            user_token_data_factory: Callable[..., UserTokenData],
    ):
        """Access и refresh токены различаются (разный jti)."""
        jwt_provider = token_provider_factory()
        user = user_token_data_factory()
        access = jwt_provider.create_token(
            CreateTokenData(user=user, refresh=False))
        refresh = jwt_provider.create_token(
            CreateTokenData(user=user, refresh=True))
        assert access != refresh


class TestDecodeToken:
    """Тесты декодирования токенов."""

    def test_decode_access_token(
            self,
            token_provider_factory: Callable[..., TokenProvider],
            user_token_data_factory: Callable[..., UserTokenData],
    ):
        """Декодированный access-токен содержит корректные данные."""
        jwt_provider = token_provider_factory()
        user = user_token_data_factory(roles=["admin"])
        token = jwt_provider.create_token(
            CreateTokenData(user=user, refresh=False)
        )

        decoded = jwt_provider.decode_token(token)
        assert decoded.user.user_id == user.user_id
        assert decoded.user.roles == ["admin"]
        assert decoded.refresh is False
        assert isinstance(decoded.jti, uuid.UUID)
        assert isinstance(decoded.exp, datetime.datetime)

    def test_decode_refresh_token(
            self,
            token_provider_factory: Callable[..., TokenProvider],
            user_token_data_factory: Callable[..., UserTokenData],
    ):
        """Декодированный refresh-токен имеет refresh=True."""
        jwt_provider = token_provider_factory()
        token = jwt_provider.create_token(
            CreateTokenData(user=user_token_data_factory(), refresh=True)
        )
        decoded = jwt_provider.decode_token(token)
        assert decoded.refresh is True

    def test_decode_preserves_superuser_flag(
            self,
            token_provider_factory: Callable[..., TokenProvider],
            user_token_data_factory: Callable[..., UserTokenData],
    ):
        """Флаг is_superuser сохраняется в токене."""
        jwt_provider = token_provider_factory()
        user = user_token_data_factory(is_superuser=True)
        token = jwt_provider.create_token(
            CreateTokenData(user=user, refresh=False)
        )
        decoded = jwt_provider.decode_token(token)
        assert decoded.user.is_superuser is True

    def test_decode_invalid_token_raises_unauthorized(
            self,
            token_provider_factory: Callable[..., TokenProvider],
    ):
        """Невалидный токен вызывает UnauthorizedError."""
        jwt_provider = token_provider_factory()
        with pytest.raises(UnauthorizedError):
            jwt_provider.decode_token("invalid.token.string")

    def test_decode_token_with_wrong_secret_raises_unauthorized(
            self,
            token_provider_factory: Callable[..., TokenProvider],
            user_token_data_factory: Callable[..., UserTokenData],
    ):
        """Токен подписанный другим секретом вызывает UnauthorizedError."""
        provider1 = token_provider_factory(secret="secret-1")
        provider2 = token_provider_factory(secret="secret-2")

        token = provider1.create_token(
            CreateTokenData(user=user_token_data_factory(), refresh=False)
        )
        with pytest.raises(UnauthorizedError):
            provider2.decode_token(token)

    def test_expired_token_raises_unauthorized(
            self,
            token_provider_factory: Callable[..., TokenProvider],
            user_token_data_factory: Callable[..., UserTokenData],
    ):
        """Истёкший токен вызывает UnauthorizedError."""
        past = datetime.datetime(2020, 1, 1)
        provider = token_provider_factory(fixed_time=past, access_minutes=1)
        token = provider.create_token(
            CreateTokenData(user=user_token_data_factory(), refresh=False)
        )
        # Токен создан в 2020 с TTL 1 минуту, уже истёк
        with pytest.raises(UnauthorizedError):
            provider.decode_token(token)


class TestBlacklist:
    """Тесты блэклиста токенов."""

    @pytest.mark.asyncio
    async def test_blacklist_and_check(
            self,
            token_provider_factory: Callable[..., TokenProvider],
    ):
        """Заблокированный JTI определяется как blacklisted."""
        cache = FakeCacheProvider()
        provider = token_provider_factory(cache=cache)
        jti = uuid.uuid4()

        assert await provider.is_token_blacklisted(jti) is False

        await provider.blacklist_token(jti)
        assert await provider.is_token_blacklisted(jti) is True

    @pytest.mark.asyncio
    async def test_non_blacklisted_token(
            self,
            token_provider_factory: Callable[..., TokenProvider],
    ):
        """Не заблокированный JTI не определяется как blacklisted."""
        cache = FakeCacheProvider()
        provider = token_provider_factory(cache=cache)

        assert await provider.is_token_blacklisted(uuid.uuid4()) is False
