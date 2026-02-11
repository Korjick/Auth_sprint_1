from internal.core.domain.models.role.role import Role
from internal.ports.input.role.list_roles_handler import (
    ListRoles,
    ListRolesHandlerProtocol,
)
from internal.ports.output.uow import UnitOfWork


class ListRolesUseCase(ListRolesHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: ListRoles) -> list[Role]:
        async with self._uow:
            roles = await self._uow.roles.list_roles()
        return roles
