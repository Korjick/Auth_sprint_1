from internal.core.domain.models.user.user import User
from internal.pkg.errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidCredentialsError, ParamEmptyError
)
from internal.ports.input.user.update_user_handler import (
    UpdateUser,
    UpdateUserHandlerProtocol,
)
from internal.ports.output.hash_provider import HashProvider
from internal.ports.output.uow import UnitOfWork


class UpdateUserUseCase(UpdateUserHandlerProtocol):
    def __init__(self, uow: UnitOfWork, hash_provider: HashProvider) -> None:
        self._uow = uow
        self._hash = hash_provider

    async def handle(self, command: UpdateUser) -> User:
        if not command.new_login:
            raise ParamEmptyError(param="new_login")

        if not command.new_password:
            raise ParamEmptyError(param="new_password")

        async with self._uow:
            user = await self._uow.users.get_user_by_login(command.login)

            if not self._hash.verify_data(user.password_hash,
                                          command.current_password):
                raise InvalidCredentialsError()

            if command.new_login != user.login:
                try:
                    await self._uow.users.get_user_by_login(command.new_login)
                    raise EntityAlreadyExistsError(
                        param="login", key=command.new_login)
                except EntityNotFoundError:
                    pass
                user = await self._uow.users.update_login(
                    user.id, command.new_login)

            if command.new_password != command.current_password:
                new_hash = self._hash.hash_data(command.new_password)
                user = await self._uow.users.update_password(
                    user.id, new_hash)

            await self._uow.commit()
            return user
