from internal.core.domain.models.user.user import User
from internal.ports.input.user.get_user_by_id_handler import (
    GetUserById,
    GetUserByIdHandlerProtocol,
)
from internal.ports.output.uow import UnitOfWork


class GetUserByIdUseCase(GetUserByIdHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetUserById) -> User:
        async with self._uow:
            user = await self._uow.users.get_user_by_id(query.user_id)
        return user
