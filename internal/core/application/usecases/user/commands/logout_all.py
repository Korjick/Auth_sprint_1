from internal.ports.input.user.logout_all_handler import (
    LogoutAll,
    LogoutAllHandlerProtocol,
)
from internal.ports.output.token_provider import TokenProvider
from internal.ports.output.uow import UnitOfWork


class LogoutAllUseCase(LogoutAllHandlerProtocol):
    def __init__(self, uow: UnitOfWork, token_provider: TokenProvider) -> None:
        self._uow = uow
        self._tokens = token_provider

    async def handle(self, command: LogoutAll) -> None:
        async with self._uow:
            await self._uow.sessions.delete_by_user_id(command.user_id)
            await self._tokens.blacklist_token(command.access_token_jti)
            await self._uow.commit()
