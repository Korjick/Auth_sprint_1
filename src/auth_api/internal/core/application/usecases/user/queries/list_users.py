from auth_api.internal.core.domain.models.user.user import User
from auth_api.internal.ports.input.user.list_users_handler import (
    ListUsersHandlerProtocol,
)
from auth_api.internal.ports.output.uow import UnitOfWork


class ListUsersUseCase(ListUsersHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self) -> list[User]:
        async with self._uow:
            users = await self._uow.users.list_users()
        return users
