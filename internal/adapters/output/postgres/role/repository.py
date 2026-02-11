import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from internal.adapters.output.postgres.role.models import Role as RoleModel
from internal.core.domain.models.role.role import Role as DomainRole, \
    ADMIN_ROLE_NAME
from internal.pkg.errors import EntityNotFoundError, ForbiddenError
from internal.ports.output.role_repository import RoleRepository, RoleCreate


class PostgresRoleRepository(RoleRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def create_role(self, role_create: RoleCreate) -> DomainRole:
        role = RoleModel(name=role_create.name)
        self._db_session.add(role)
        await self._db_session.flush()
        return DomainRole(oid=role.id, name=role.name)

    async def update_role(self, role_id: uuid.UUID, name: str) -> DomainRole:
        result = await self._db_session.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(param="id", key=str(role_id))

        if row.name == ADMIN_ROLE_NAME:
            raise ForbiddenError()

        row.name = name
        await self._db_session.flush()
        return DomainRole(oid=row.id, name=row.name)

    async def delete_role(self, role_id: uuid.UUID) -> None:
        result = await self._db_session.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(param="id", key=str(role_id))

        if row.name == ADMIN_ROLE_NAME:
            raise ForbiddenError()

        await self._db_session.execute(
            delete(RoleModel).where(RoleModel.id == role_id)
        )
        await self._db_session.flush()

    async def get_role_by_id(self, role_id: uuid.UUID) -> DomainRole:
        result = await self._db_session.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(param="id", key=str(role_id))
        return DomainRole(oid=row.id, name=row.name)

    async def list_roles(self) -> list[DomainRole]:
        result = await self._db_session.execute(select(RoleModel))
        rows = result.scalars().all()
        return [DomainRole(oid=row.id, name=row.name) for row in rows]
