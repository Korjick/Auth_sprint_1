from internal.core.domain.models.session.session import Session
from internal.pkg.errors import EntityNotFoundError, InvalidCredentialsError
from internal.ports.input.user.login_user_handler import (
    LoginUserHandlerProtocol,
    LoginUser,
    LoggedInUser,
)
from internal.ports.output.hash_provider import HashProvider
from internal.ports.output.session_repository import SessionCreate
from internal.ports.output.token_provider import (
    TokenProvider,
    CreateTokenData,
    UserTokenData,
)
from internal.ports.output.uow import UnitOfWork


class LoginUserUseCase(LoginUserHandlerProtocol):
    def __init__(
            self,
            uow: UnitOfWork,
            password_hasher: HashProvider,
            token_provider: TokenProvider,
    ):
        self._uow = uow
        self._hasher = password_hasher
        self._tokens = token_provider

    async def handle(self, command: LoginUser) -> LoggedInUser:
        command.login = command.login.strip()
        async with self._uow:
            try:
                user = await self._uow.users.get_user_by_login(command.login)
            except EntityNotFoundError:
                raise InvalidCredentialsError()

            if not self._hasher.verify_data(
                    user.password_hash, command.password):
                raise InvalidCredentialsError()

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

            # Find existing session for this device
            sessions = await self._uow.sessions.get_sessions_by_user_id(
                user_id=user.id)
            found_session = None
            for session in sessions:
                if session.device_fingerprint == command.device_fingerprint:
                    found_session = session
                    break

            if found_session:
                await self._uow.sessions.update_session(Session(
                    oid=found_session.id,
                    user_id=found_session.user_id,
                    device_fingerprint=found_session.device_fingerprint,
                    expire_at=decoded_refresh.exp,
                    jti=decoded_refresh.jti,
                ))
            else:
                await self._uow.sessions.create_session(SessionCreate(
                    user_id=user.id,
                    device_fingerprint=command.device_fingerprint,
                    expires_at=decoded_refresh.exp,
                    jti=decoded_refresh.jti,
                ))
            await self._uow.commit()

            return LoggedInUser(
                access_session=access_token,
                refresh_session=refresh_token,
            )
