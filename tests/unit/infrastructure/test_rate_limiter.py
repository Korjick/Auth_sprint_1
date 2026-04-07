import datetime

import pytest

from auth_api.internal.infrastructure.rate_limiter import (
    RedisFixedWindowRateLimiter,
)
from auth_api.internal.pkg.errors import InfrastructureError
from auth_api.internal.ports.output.rate_limiter import (
    FixedWindowLimit,
    RateLimitConfig,
)
from tests.unit.fakes import FakeLogger, FakeRedis, FakeTimeProvider


def _rate_limit_config() -> RateLimitConfig:
    return RateLimitConfig(
        enabled=True,
        api_ip=FixedWindowLimit(limit=300, window_sec=60),
        signup_ip=FixedWindowLimit(limit=10, window_sec=60),
        login_ip=FixedWindowLimit(limit=30, window_sec=60),
        login_key_ip=FixedWindowLimit(limit=5, window_sec=60),
        refresh_user=FixedWindowLimit(limit=30, window_sec=60),
    )


def _time_provider(unix_ts: int) -> FakeTimeProvider:
    return FakeTimeProvider(
        datetime.datetime.fromtimestamp(unix_ts, datetime.timezone.utc)
    )


class TestRedisFixedWindowRateLimiter:
    @pytest.mark.asyncio
    async def test_allows_request_within_limit(self):
        fake_redis = FakeRedis(result=[3, 55])
        fake_logger = FakeLogger()
        limiter = RedisFixedWindowRateLimiter(
            redis_client=fake_redis,
            project_name="auth",
            logger=fake_logger,
            config=_rate_limit_config(),
            time_provider=_time_provider(1000),
        )

        decision = await limiter.hit("login_ip:127.0.0.1", limit=5, window_sec=60)

        assert decision.allowed is True
        assert decision.limit == 5
        assert decision.remaining == 2
        assert decision.retry_after == 0
        assert decision.reset_at == 1055
        assert len(fake_redis.calls) == 7
        assert fake_redis.calls[0] == ("pipeline", True)
        assert fake_redis.calls[1] == ("pipeline_enter",)
        assert fake_redis.calls[2] == (
            "incr",
            "auth:rate_limit:login_ip:127.0.0.1",
        )
        assert fake_redis.calls[3] == (
            "expire",
            "auth:rate_limit:login_ip:127.0.0.1",
            60,
            True,
            False,
            False,
            False,
        )
        assert fake_redis.calls[4] == (
            "ttl",
            "auth:rate_limit:login_ip:127.0.0.1",
        )
        assert fake_redis.calls[5] == ("execute",)
        assert fake_redis.calls[6] == ("pipeline_exit",)

    @pytest.mark.asyncio
    async def test_blocks_request_after_limit(self):
        fake_redis = FakeRedis(result=[7, 19])
        limiter = RedisFixedWindowRateLimiter(
            redis_client=fake_redis,
            project_name="auth",
            logger=FakeLogger(),
            config=_rate_limit_config(),
            time_provider=_time_provider(2000),
        )

        decision = await limiter.hit("signup_ip:127.0.0.1", limit=5, window_sec=60)

        assert decision.allowed is False
        assert decision.remaining == 0
        assert decision.retry_after == 19
        assert decision.reset_at == 2019

    @pytest.mark.asyncio
    async def test_fail_open_when_redis_unavailable(self):
        fake_logger = FakeLogger()
        limiter = RedisFixedWindowRateLimiter(
            redis_client=FakeRedis(exc=RuntimeError("redis down")),
            project_name="auth",
            logger=fake_logger,
            config=_rate_limit_config(),
            time_provider=_time_provider(3000),
            fail_open=True,
        )

        decision = await limiter.hit("api_ip:127.0.0.1", limit=10, window_sec=60)

        assert decision.allowed is True
        assert decision.remaining == 9
        assert decision.retry_after == 0
        assert decision.reset_at == 3060
        assert fake_logger.events[0][0] == "rate_limiter_unavailable"

    @pytest.mark.asyncio
    async def test_fail_closed_when_redis_unavailable(self):
        limiter = RedisFixedWindowRateLimiter(
            redis_client=FakeRedis(exc=RuntimeError("redis down")),
            project_name="auth",
            logger=FakeLogger(),
            config=_rate_limit_config(),
            time_provider=_time_provider(3000),
            fail_open=False,
        )

        with pytest.raises(InfrastructureError):
            await limiter.hit("api_ip:127.0.0.1", limit=10, window_sec=60)
