from internal.pkg.errors import ForbiddenError
from internal.ports.input.user.refresh_session_handler import (
    RefreshSession,
    RefreshSessionHandlerProtocol,
    LoggedInUser,
)
from internal.ports.output.time_provider import TimeProvider
from internal.ports.output.token_provider import (
    CreateTokenData,
    TokenProvider,
    UserTokenData,
)
from internal.ports.output.uow import UnitOfWork


class RefreshSessionUseCase(RefreshSessionHandlerProtocol):
    def __init__(self,
                 token_provider: TokenProvider,
                 uow: UnitOfWork,
                 time_provider: TimeProvider) -> None:
        self._tokens = token_provider
        self._uow = uow
        self._time = time_provider

    async def handle(self, refresh_session: RefreshSession) \
            -> LoggedInUser:
        refresh_session.user.login = refresh_session.user.login.strip()
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
            user_token = UserTokenData(
                login=user.login,
                roles=user.roles,
                is_superuser=user.is_superuser,
            )

            access_token = self._tokens.create_token(
                CreateTokenData(user=user_token, refresh=False)
            )
            refresh_token = self._tokens.create_token(
                CreateTokenData(user=user_token, refresh=True)
            )

            decoded_refresh = self._tokens.decode_token(refresh_token)
            session.jti = decoded_refresh.jti
            session.expire_at = decoded_refresh.exp
            await self._uow.sessions.update_session(session)
            await self._uow.commit()

        return LoggedInUser(access_session=access_token,
                            refresh_session=refresh_token)
