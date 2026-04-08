from redis.asyncio import Redis

from auth_api.internal.ports.output.cache_provider import CacheProvider


class RedisCacheProvider(CacheProvider):
    def __init__(self, redis_client: Redis, project_name: str):
        self.redis_client = redis_client
        self.project_name = project_name

    async def cache_data(self, key: str, data: str | int | float,
                         expire_sec: int):
        await self.redis_client.set(name=f"{self.project_name}:{key}",
                                    value=data, ex=expire_sec)

    async def get_from_cache(self, key: str) -> str | int | float | None:
        return await self.redis_client.get(name=f"{self.project_name}:{key}")

    async def pop_from_cache(self, key: str) -> str | int | float | None:
        return await self.redis_client.getdel(name=f"{self.project_name}:{key}")

