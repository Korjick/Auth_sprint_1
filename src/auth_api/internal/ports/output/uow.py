import typing

from auth_api.internal.ports.output.session_repository import SessionRepository
from auth_api.internal.ports.output.social_identity_repository import (
    SocialIdentityRepository,
)
from auth_api.internal.ports.output.user_repository import UserRepository
from auth_api.internal.ports.output.role_repository import RoleRepository


class UnitOfWork(typing.Protocol):
    users: UserRepository
    sessions: SessionRepository
    roles: RoleRepository
    social_identities: SocialIdentityRepository

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    async def commit(self):
        ...

    async def rollback(self):
        ...

