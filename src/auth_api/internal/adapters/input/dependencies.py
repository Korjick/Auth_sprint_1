from fastapi import Request

from auth_api.internal.ports.output.hash_provider import HashProvider
from auth_api.internal.ports.output.logger import Logger
from auth_api.internal.ports.output.rate_limiter import RateLimiter
from auth_api.internal.ports.output.cache_provider import CacheProvider
from auth_api.internal.ports.output.social_auth_provider import SocialAuthProvider
from auth_api.internal.ports.output.time_provider import TimeProvider
from auth_api.internal.ports.output.token_provider import TokenProvider
from auth_api.internal.ports.output.uow import UnitOfWork


def get_token_provider(request: Request) -> TokenProvider:
    return request.app.state.token_provider


def get_hash_provider(request: Request) -> HashProvider:
    return request.app.state.hash_provider


def get_uow(request: Request) -> UnitOfWork:
    return request.app.state.uow


def get_time_provider(request: Request) -> TimeProvider:
    return request.app.state.time_provider


def get_logger(request: Request) -> Logger:
    return request.app.state.logger


def get_rate_limiter(request: Request) -> RateLimiter:
    return request.app.state.rate_limiter


def get_cache_provider(request: Request) -> CacheProvider:
    return request.app.state.cache_provider


def get_google_social_auth_provider(request: Request) -> SocialAuthProvider:
    return request.app.state.google_social_auth_provider
