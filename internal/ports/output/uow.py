import typing

from internal.ports.output.session_repository import SessionRepository
from internal.ports.output.user_repository import UserRepository
from internal.ports.output.role_repository import RoleRepository


class UnitOfWork(typing.Protocol):
    users: UserRepository
    sessions: SessionRepository
    roles: RoleRepository

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    async def commit(self):
        ...

    async def rollback(self):
        ...
