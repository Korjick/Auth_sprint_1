import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from internal.adapters.output.postgres.user.models import User as UserModel
from internal.adapters.output.postgres.role.models import Role as RoleModel
from internal.core.domain.models.user.user import User as DomainUser
from internal.pkg.errors import EntityNotFoundError
from internal.ports.output.user_repository import UserRepository, UserCreate


class PostgresUserRepository(UserRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    @staticmethod
    def _to_domain(user: UserModel) -> DomainUser:
        return DomainUser(
            oid=user.id,
            login=user.login,
            password_hash=user.password_hash,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=[role.name for role in user.roles],
            is_superuser=user.is_superuser,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    async def save_user(self, user_to_create: UserCreate) -> DomainUser:
        user = UserModel(
            login=user_to_create.login,
            first_name=user_to_create.first_name,
            last_name=user_to_create.last_name,
            password_hash=user_to_create.password_hash,
        )
        user.is_superuser = user_to_create.is_superuser
        user.is_active = user_to_create.is_active
        self._db_session.add(user)
        await self._db_session.flush()
        await self._db_session.refresh(user, attribute_names=["roles"])
        return self._to_domain(user)

    async def get_user_by_login(self, login: str) -> DomainUser:
        result = await self._db_session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.login == login)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(param="login", key=login)
        return self._to_domain(row)

    async def update_login(self, user_id: uuid.UUID,
                           new_login: str) -> DomainUser:
        result = await self._db_session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.id == user_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(param="id", key=str(user_id))
        row.login = new_login
        await self._db_session.flush()
        return self._to_domain(row)

    async def update_password(self, user_id: uuid.UUID,
                              new_password_hash: str) -> DomainUser:
        result = await self._db_session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.id == user_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(param="id", key=str(user_id))
        row.password_hash = new_password_hash
        await self._db_session.flush()
        return self._to_domain(row)

    async def add_role(self, user_id: uuid.UUID,
                       role_id: uuid.UUID) -> DomainUser:
        result = await self._db_session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.id == user_id)
        )
        user_row = result.scalar_one_or_none()
        if user_row is None:
            raise EntityNotFoundError(param="id", key=str(user_id))

        result = await self._db_session.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        role_row = result.scalar_one_or_none()
        if role_row is None:
            raise EntityNotFoundError(param="role_id", key=str(role_id))

        if role_row not in user_row.roles:
            user_row.roles.append(role_row)
        await self._db_session.flush()
        return self._to_domain(user_row)

    async def remove_role(self, user_id: uuid.UUID,
                          role_id: uuid.UUID) -> DomainUser:
        result = await self._db_session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.id == user_id)
        )
        user_row = result.scalar_one_or_none()
        if user_row is None:
            raise EntityNotFoundError(param="id", key=str(user_id))

        result = await self._db_session.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        role_row = result.scalar_one_or_none()
        if role_row is None:
            raise EntityNotFoundError(param="role_id", key=str(role_id))

        if role_row in user_row.roles:
            user_row.roles.remove(role_row)
        await self._db_session.flush()
        return self._to_domain(user_row)
