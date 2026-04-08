import datetime

from auth_api.internal.ports.output.cache_provider import CacheProvider
from auth_api.internal.ports.output.time_provider import TimeProvider


class FakeCacheProvider(CacheProvider):
    def __init__(self):
        self._store: dict[str, str] = {}

    async def cache_data(self, key: str, data: str | int | float,
                         expire_sec: int):
        self._store[key] = str(data)

    async def get_from_cache(self, key: str) -> str | None:
        return self._store.get(key)

    async def pop_from_cache(self, key: str) -> str | None:
        return self._store.pop(key, None)


class FakeTimeProvider(TimeProvider):
    def __init__(self, fixed_now: datetime.datetime | None = None):
        if fixed_now is None:
            self._now = datetime.datetime.now(datetime.timezone.utc)
        elif fixed_now.tzinfo is None:
            self._now = fixed_now.replace(tzinfo=datetime.timezone.utc)
        else:
            self._now = fixed_now.astimezone(datetime.timezone.utc)

    def now_utc(self) -> datetime.datetime:
        return self._now

    def from_timestamp(self, timestamp: int | float) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(
            timestamp,
            datetime.timezone.utc,
        )


class FakeLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def warning(self, event: str, **fields) -> None:
        self.events.append((event, fields))


class FakeRedisPipeline:
    def __init__(self, redis: "FakeRedis") -> None:
        self._redis = redis

    async def __aenter__(self) -> "FakeRedisPipeline":
        self._redis.calls.append(("pipeline_enter",))
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._redis.calls.append(("pipeline_exit",))

    def incr(self, key: str):
        self._redis.calls.append(("incr", key))
        return self

    def expire(
            self,
            key: str,
            window_sec: int,
            nx: bool = False,
            xx: bool = False,
            gt: bool = False,
            lt: bool = False,
    ):
        self._redis.calls.append(
            ("expire", key, window_sec, nx, xx, gt, lt)
        )
        return self

    def ttl(self, key: str):
        self._redis.calls.append(("ttl", key))
        return self

    async def execute(self):
        self._redis.calls.append(("execute",))
        if self._redis.exc:
            raise self._redis.exc
        current, ttl = self._redis.result
        return [current, True, ttl]


class FakeRedis:
    def __init__(
            self,
            result: tuple[int, int] | list[int] = (0, 0),
            exc: Exception | None = None,
    ) -> None:
        self.result = result
        self.exc = exc
        self.calls: list[tuple] = []

    def pipeline(self, transaction: bool = True) -> FakeRedisPipeline:
        self.calls.append(("pipeline", transaction))
        return FakeRedisPipeline(self)
