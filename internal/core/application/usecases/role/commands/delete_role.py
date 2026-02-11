from internal.ports.input.role.delete_role_handler import (
    DeleteRole,
    DeleteRoleHandlerProtocol,
)
from internal.ports.output.uow import UnitOfWork


class DeleteRoleUseCase(DeleteRoleHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: DeleteRole) -> None:
        async with self._uow:
            await self._uow.roles.delete_role(command.role_id)
            await self._uow.commit()
