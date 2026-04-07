from auth_api.internal.core.domain.models.role.role import Role
from auth_api.internal.ports.input.role.update_role_handler import (
    UpdateRole,
    UpdateRoleHandlerProtocol,
)
from auth_api.internal.ports.output.uow import UnitOfWork


class UpdateRoleUseCase(UpdateRoleHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: UpdateRole) -> Role:
        command.name = command.name.strip()
        async with self._uow:
            role = await self._uow.roles.update_role(command.role_id,
                                                     command.name)
            await self._uow.commit()
            return role

