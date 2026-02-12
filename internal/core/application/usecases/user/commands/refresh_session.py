from internal.core.application.services.token_pair import \
    TokenPairService
from internal.pkg.errors import ForbiddenError
from internal.ports.input.user.refresh_session_handler import (
    RefreshSession,
    RefreshSessionHandlerProtocol,
    LoggedInUser,
)
from internal.ports.output.time_provider import TimeProvider
from internal.ports.output.uow import UnitOfWork


class RefreshSessionUseCase(RefreshSessionHandlerProtocol):
    def __init__(self,
                 token_pair_service: TokenPairService,
                 uow: UnitOfWork,
                 time_provider: TimeProvider) -> None:
        self._token_pair_service = token_pair_service
        self._uow = uow
        self._time = time_provider

    async def handle(self, refresh_session: RefreshSession) \
            -> LoggedInUser:
        now = self._time.now_utc()
        async with self._uow:
            session = await self._uow.sessions.get_session_by_jti(
                jti=refresh_session.jti)
            if session.expire_at < now:
                raise ForbiddenError()

            if session.device_fingerprint != \
                    refresh_session.device_fingerprint:
                raise ForbiddenError()

            user = await self._uow.users.get_user_by_login(
                refresh_session.user.login
            )
            token_pair = self._token_pair_service.create_for_user(user)
            session.jti = token_pair.refresh_token.jti
            session.expire_at = token_pair.refresh_token.exp
            await self._uow.sessions.update_session(session)
            await self._uow.commit()

        return LoggedInUser(access_session=token_pair.access_token.token,
                            refresh_session=token_pair.refresh_token.token)
