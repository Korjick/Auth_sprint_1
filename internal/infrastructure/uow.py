from sqlalchemy.ext.asyncio import async_sessionmaker

from internal.adapters.output.postgres.session.repository import \
    PostgresSessionRepository
from internal.adapters.output.postgres.role.repository import \
    PostgresRoleRepository
from internal.adapters.output.postgres.user.repository import \
    PostgresUserRepository
from internal.ports.output.session_repository import SessionRepository
from internal.ports.output.uow import UnitOfWork
from internal.ports.output.user_repository import UserRepository
from internal.ports.output.role_repository import RoleRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    users: UserRepository
    sessions: SessionRepository
    roles: RoleRepository

    def __init__(self,
                 db_session_factory: async_sessionmaker):
        self.db_session_factory = db_session_factory

    async def __aenter__(self):
        self.db_session = self.db_session_factory()
        self.users = PostgresUserRepository(self.db_session)
        self.sessions = PostgresSessionRepository(self.db_session)
        self.roles = PostgresRoleRepository(self.db_session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.db_session.close()

    async def commit(self):
        await self.db_session.commit()

    async def rollback(self):
        await self.db_session.rollback()
