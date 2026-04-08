import typing


class CacheProvider(typing.Protocol):
    async def cache_data(self, key: str, data: str | int | float,
                         expire_sec: int):
        ...

    async def get_from_cache(self, key: str) -> str | int | float | None:
        ...

    async def pop_from_cache(self, key: str) -> str | int | float | None:
        ...
