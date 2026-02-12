import datetime

from internal.ports.output.cache_provider import CacheProvider
from internal.ports.output.time_provider import TimeProvider


class FakeCacheProvider(CacheProvider):
    """In-memory заглушка для CacheProvider."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def cache_data(self, key: str, data: str | int | float,
                         expire_sec: int):
        self._store[key] = str(data)

    async def get_from_cache(self, key: str) -> str | None:
        return self._store.get(key)


class FakeTimeProvider(TimeProvider):
    """Детерминированный TimeProvider для тестов."""

    def __init__(self, fixed_now: datetime.datetime | None = None):
        self._now = fixed_now or datetime.datetime.now(
            datetime.timezone.utc).replace(tzinfo=None)

    def now_utc(self) -> datetime.datetime:
        return self._now

    def from_timestamp(self, timestamp: int | float) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(timestamp).replace(tzinfo=None)
