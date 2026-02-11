from internal.ports.input.user.logout_user_handler import (
    Logout,
    LogoutHandlerProtocol,
)
from internal.ports.output.token_provider import TokenProvider
from internal.ports.output.uow import UnitOfWork


class LogoutUserUseCase(LogoutHandlerProtocol):
    def __init__(
            self,
            uow: UnitOfWork,
            token_provider: TokenProvider,
    ) -> None:
        self._uow = uow
        self._tokens = token_provider

    async def handle(self, command: Logout) -> None:
        command.login = command.login.strip()
        async with self._uow:
            user = await self._uow.users.get_user_by_login(command.login)
            if user is None:
                return
            await self._uow.sessions.delete_by_user_id_and_fingerprint(
                user_id=user.id,
                device_fingerprint=command.device_fingerprint,
            )
            if command.access_token_jti:
                await self._tokens.blacklist_token(command.access_token_jti)
            await self._uow.commit()
