from internal.core.domain.models.user.user import User
from internal.ports.input.user.assign_role_handler import (
    AssignRole,
    AssignRoleHandlerProtocol,
)
from internal.ports.output.uow import UnitOfWork


class AssignRoleUseCase(AssignRoleHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: AssignRole) -> User:
        command.user_login = command.user_login.strip()
        async with self._uow:
            user = await self._uow.users.get_user_by_login(
                command.user_login
            )
            user = await self._uow.users.add_role(user.id, command.role_id)
            await self._uow.commit()
            return user
