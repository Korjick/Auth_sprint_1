import pytest

from auth_api.internal.adapters.output.redis.cache_provider import RedisCacheProvider


@pytest.fixture
def cache_provider(redis_client) -> RedisCacheProvider:
    """РџСЂРѕРІР°Р№РґРµСЂ РєСЌС€Р° СЃ С‚РµСЃС‚РѕРІС‹Рј Redis-РєР»РёРµРЅС‚РѕРј."""
    return RedisCacheProvider(redis_client=redis_client,
                              project_name="test_auth")


class TestRedisCacheProvider:
    """РўРµСЃС‚С‹ Redis-РєСЌС€ РїСЂРѕРІР°Р№РґРµСЂР°."""

    @pytest.mark.asyncio
    async def test_cache_and_retrieve_string(self, cache_provider):
        """РЎС‚СЂРѕРєРѕРІРѕРµ Р·РЅР°С‡РµРЅРёРµ СЃРѕС…СЂР°РЅСЏРµС‚СЃСЏ Рё РґРѕСЃС‚Р°С‘С‚СЃСЏ РёР· РєСЌС€Р°."""
        await cache_provider.cache_data("key1", "value1", expire_sec=60)
        result = await cache_provider.get_from_cache("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_cache_and_retrieve_integer(self, cache_provider):
        """Р§РёСЃР»РѕРІРѕРµ Р·РЅР°С‡РµРЅРёРµ СЃРѕС…СЂР°РЅСЏРµС‚СЃСЏ Рё РґРѕСЃС‚Р°С‘С‚СЃСЏ РёР· РєСЌС€Р°."""
        await cache_provider.cache_data("count", 42, expire_sec=60)
        result = await cache_provider.get_from_cache("count")
        assert result == "42"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key_returns_none(self, cache_provider):
        """РќРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РёР№ РєР»СЋС‡ РІРѕР·РІСЂР°С‰Р°РµС‚ None."""
        result = await cache_provider.get_from_cache("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_overwrite_value(self, cache_provider):
        """РџРµСЂРµР·Р°РїРёСЃСЊ Р·РЅР°С‡РµРЅРёСЏ РїРѕ С‚РѕРјСѓ Р¶Рµ РєР»СЋС‡Сѓ."""
        await cache_provider.cache_data("mykey", "old", expire_sec=60)
        await cache_provider.cache_data("mykey", "new", expire_sec=60)
        result = await cache_provider.get_from_cache("mykey")
        assert result == "new"

    @pytest.mark.asyncio
    async def test_project_name_prefix(self, cache_provider, redis_client):
        """РљР»СЋС‡Рё С…СЂР°РЅСЏС‚СЃСЏ СЃ РїСЂРµС„РёРєСЃРѕРј project_name."""
        await cache_provider.cache_data("prefixed", "val", expire_sec=60)
        # РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ РІ Redis РєР»СЋС‡ СЃ РїРѕР»РЅС‹Рј РёРјРµРЅРµРј
        raw = await redis_client.get("test_auth:prefixed")
        assert raw == "val"

