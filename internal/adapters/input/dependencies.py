from fastapi import Request

from internal.ports.output.hash_provider import HashProvider
from internal.ports.output.time_provider import TimeProvider
from internal.ports.output.token_provider import TokenProvider
from internal.ports.output.uow import UnitOfWork


def get_token_provider(request: Request) -> TokenProvider:
    return request.app.state.token_provider


def get_hash_provider(request: Request) -> HashProvider:
    return request.app.state.hash_provider


def get_uow(request: Request) -> UnitOfWork:
    return request.app.state.uow


def get_time_provider(request: Request) -> TimeProvider:
    return request.app.state.time_provider
