from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    reset_at: int
    retry_after: int


@dataclass(frozen=True, slots=True)
class FixedWindowLimit:
    limit: int
    window_sec: int


@dataclass(frozen=True, slots=True)
class RateLimitConfig:
    enabled: bool
    api_ip: FixedWindowLimit
    signup_ip: FixedWindowLimit
    login_ip: FixedWindowLimit
    login_key_ip: FixedWindowLimit
    refresh_user: FixedWindowLimit


class RateLimiter(Protocol):
    @property
    def config(self) -> RateLimitConfig:
        ...

    async def hit(
            self,
            key: str,
            limit: int,
            window_sec: int,
    ) -> RateLimitDecision:
        ...
