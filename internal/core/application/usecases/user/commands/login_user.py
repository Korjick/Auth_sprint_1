from internal.core.domain.models.session.session import Session
from internal.core.application.services.token_pair import \
    TokenPairService
from internal.pkg.errors import EntityNotFoundError, InvalidCredentialsError
from internal.ports.input.user.login_user_handler import (
    LoginUserHandlerProtocol,
    LoginUser,
    LoggedInUser,
)
from internal.ports.output.hash_provider import HashProvider
from internal.ports.output.session_repository import SessionCreate
from internal.ports.output.uow import UnitOfWork


class LoginUserUseCase(LoginUserHandlerProtocol):
    def __init__(
            self,
            uow: UnitOfWork,
            password_hasher: HashProvider,
            token_pair_service: TokenPairService,
    ):
        self._uow = uow
        self._hasher = password_hasher
        self._token_pair_service = token_pair_service

    async def handle(self, command: LoginUser) -> LoggedInUser:
        async with self._uow:
            try:
                user = await self._uow.users.get_user_by_login(command.login)
            except EntityNotFoundError:
                raise InvalidCredentialsError()

            if not self._hasher.verify_data(
                    user.password_hash, command.password):
                raise InvalidCredentialsError()

            token_pair = self._token_pair_service.create_for_user(user)

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
                    expire_at=token_pair.refresh_token.exp,
                    jti=token_pair.refresh_token.jti,
                ))
            else:
                await self._uow.sessions.create_session(SessionCreate(
                    user_id=user.id,
                    device_fingerprint=command.device_fingerprint,
                    expires_at=token_pair.refresh_token.exp,
                    jti=token_pair.refresh_token.jti,
                ))
            await self._uow.commit()

            return LoggedInUser(
                access_session=token_pair.access_token.token,
                refresh_session=token_pair.refresh_token.token,
            )
