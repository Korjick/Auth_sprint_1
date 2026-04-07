from redis.asyncio import Redis

from auth_api.internal.pkg.errors import InfrastructureError
from auth_api.internal.ports.output.logger import Logger
from auth_api.internal.ports.output.rate_limiter import (
    RateLimitConfig,
    RateLimitDecision,
    RateLimiter,
)
from auth_api.internal.ports.output.time_provider import TimeProvider


class RedisFixedWindowRateLimiter(RateLimiter):
    def __init__(
            self,
            redis_client: Redis,
            project_name: str,
            logger: Logger,
            config: RateLimitConfig,
            time_provider: TimeProvider,
            fail_open: bool = True,
    ) -> None:
        self._redis = redis_client
        self._prefix = f"{project_name}:rate_limit"
        self._logger = logger
        self._config = config
        self._fail_open = fail_open
        self._time_provider = time_provider

    @property
    def config(self) -> RateLimitConfig:
        return self._config

    async def hit(
            self,
            key: str,
            limit: int,
            window_sec: int,
    ) -> RateLimitDecision:
        now = int(self._time_provider.now_utc().timestamp())
        redis_key = f"{self._prefix}:{key}"
        try:
            async with self._redis.pipeline(transaction=True) as pipe:
                pipe.incr(redis_key)
                pipe.expire(redis_key, window_sec, nx=True)
                pipe.ttl(redis_key)
                current_raw, _, ttl_raw = await pipe.execute()
            current = int(current_raw)
            ttl = int(ttl_raw)
        except Exception as exc:
            self._logger.warning(
                "rate_limiter_unavailable",
                key=key,
                error=type(exc).__name__,
                fail_open=self._fail_open,
            )
            if self._fail_open:
                return RateLimitDecision(
                    allowed=True,
                    limit=limit,
                    remaining=max(limit - 1, 0),
                    reset_at=now + window_sec,
                    retry_after=0,
                )
            raise InfrastructureError(service="redis", cause=exc) from exc

        if ttl < 0:
            ttl = window_sec
        remaining = max(limit - current, 0)
        retry_after = ttl if current > limit else 0
        return RateLimitDecision(
            allowed=current <= limit,
            limit=limit,
            remaining=remaining,
            reset_at=now + ttl,
            retry_after=retry_after,
        )
