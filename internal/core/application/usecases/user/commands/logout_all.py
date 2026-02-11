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
        command.login = command.login.strip()
        async with self._uow:
            user = await self._uow.users.get_user_by_login(command.login)
            await self._uow.sessions.delete_by_user_id(user.id)
            await self._tokens.blacklist_token(command.access_token_jti)
            await self._uow.commit()
