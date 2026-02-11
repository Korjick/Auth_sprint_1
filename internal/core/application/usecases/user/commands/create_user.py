from internal.core.domain.models.user.user import User
from internal.ports.input.user.create_user_handler import (
    CreateUser,
    CreateUserHandlerProtocol,
)
from internal.ports.output.hash_provider import HashProvider
from internal.ports.output.uow import UnitOfWork
from internal.ports.output.user_repository import UserCreate


class CreateUserUseCase(CreateUserHandlerProtocol):
    def __init__(
            self,
            uow: UnitOfWork,
            password_hasher: HashProvider
    ) -> None:
        self._uow = uow
        self._password_hasher = password_hasher

    async def handle(self, command: CreateUser) -> User:
        command.login = command.login.strip()
        command.first_name = command.first_name.strip()
        command.last_name = command.last_name.strip()
        hashed_password = self._password_hasher.hash_data(command.password)
        user_to_create = UserCreate(
            login=command.login,
            password_hash=hashed_password,
            first_name=command.first_name,
            last_name=command.last_name,
            is_superuser=command.is_superuser,
            is_active=command.is_active,
        )
        async with self._uow:
            user = await self._uow.users.save_user(user_to_create)
            await self._uow.commit()
            return user
