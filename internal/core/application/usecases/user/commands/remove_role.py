from internal.core.domain.models.user.user import User
from internal.ports.input.user.remove_role_handler import (
    RemoveRole,
    RemoveRoleHandlerProtocol,
)
from internal.ports.output.uow import UnitOfWork


class RemoveRoleUseCase(RemoveRoleHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: RemoveRole) -> User:
        async with self._uow:
            user = await self._uow.users.remove_role(command.user_id,
                                                     command.role_id)
            await self._uow.commit()
            return user
