from internal.core.domain.models.user.user import User
from internal.ports.input.user.get_user_by_login_handler import (
    GetUserByLogin,
    GetUserByLoginHandlerProtocol,
)
from internal.ports.output.uow import UnitOfWork


class GetUserByLoginUseCase(GetUserByLoginHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetUserByLogin) -> User:
        async with self._uow:
            user = await self._uow.users.get_user_by_login(query.login)
        return user
