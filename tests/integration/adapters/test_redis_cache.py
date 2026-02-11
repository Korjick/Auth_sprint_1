import pytest

from internal.adapters.output.redis.cache_provider import RedisCacheProvider


@pytest.fixture
def cache_provider(redis_client) -> RedisCacheProvider:
    """Провайдер кэша с тестовым Redis-клиентом."""
    return RedisCacheProvider(redis_client=redis_client,
                              project_name="test_auth")


class TestRedisCacheProvider:
    """Тесты Redis-кэш провайдера."""

    @pytest.mark.asyncio
    async def test_cache_and_retrieve_string(self, cache_provider):
        """Строковое значение сохраняется и достаётся из кэша."""
        await cache_provider.cache_data("key1", "value1", expire_sec=60)
        result = await cache_provider.get_from_cache("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_cache_and_retrieve_integer(self, cache_provider):
        """Числовое значение сохраняется и достаётся из кэша."""
        await cache_provider.cache_data("count", 42, expire_sec=60)
        result = await cache_provider.get_from_cache("count")
        assert result == "42"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key_returns_none(self, cache_provider):
        """Несуществующий ключ возвращает None."""
        result = await cache_provider.get_from_cache("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_overwrite_value(self, cache_provider):
        """Перезапись значения по тому же ключу."""
        await cache_provider.cache_data("mykey", "old", expire_sec=60)
        await cache_provider.cache_data("mykey", "new", expire_sec=60)
        result = await cache_provider.get_from_cache("mykey")
        assert result == "new"

    @pytest.mark.asyncio
    async def test_project_name_prefix(self, cache_provider, redis_client):
        """Ключи хранятся с префиксом project_name."""
        await cache_provider.cache_data("prefixed", "val", expire_sec=60)
        # Проверяем, что в Redis ключ с полным именем
        raw = await redis_client.get("test_auth:prefixed")
        assert raw == "val"
