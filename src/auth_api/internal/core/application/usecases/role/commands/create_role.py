from auth_api.internal.core.domain.models.role.role import Role
from auth_api.internal.ports.input.role.create_role_handler import (
    CreateRole,
    CreateRoleHandlerProtocol,
)
from auth_api.internal.ports.output.role_repository import RoleCreate
from auth_api.internal.ports.output.uow import UnitOfWork


class CreateRoleUseCase(CreateRoleHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: CreateRole) -> Role:
        command.name = command.name.strip()
        async with self._uow:
            role = await self._uow.roles.create_role(
                RoleCreate(name=command.name)
            )
            await self._uow.commit()
            return role

