from sqlalchemy.ext.asyncio import async_sessionmaker

from auth_api.internal.adapters.output.postgres.role.repository import \
    PostgresRoleRepository
from auth_api.internal.adapters.output.postgres.session.repository import \
    PostgresSessionRepository
from auth_api.internal.adapters.output.postgres.social_identity.repository import \
    PostgresSocialIdentityRepository
from auth_api.internal.adapters.output.postgres.user.repository import \
    PostgresUserRepository
from auth_api.internal.ports.output.role_repository import RoleRepository
from auth_api.internal.ports.output.session_repository import SessionRepository
from auth_api.internal.ports.output.social_identity_repository import (
    SocialIdentityRepository,
)
from auth_api.internal.ports.output.uow import UnitOfWork
from auth_api.internal.ports.output.user_repository import UserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    users: UserRepository
    sessions: SessionRepository
    roles: RoleRepository
    social_identities: SocialIdentityRepository

    def __init__(self,
                 db_session_factory: async_sessionmaker):
        self.db_session_factory = db_session_factory

    async def __aenter__(self):
        self.db_session = self.db_session_factory()
        self.users = PostgresUserRepository(self.db_session)
        self.sessions = PostgresSessionRepository(self.db_session)
        self.roles = PostgresRoleRepository(self.db_session)
        self.social_identities = PostgresSocialIdentityRepository(
            self.db_session
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.db_session.close()

    async def commit(self):
        await self.db_session.commit()

    async def rollback(self):
        await self.db_session.rollback()

