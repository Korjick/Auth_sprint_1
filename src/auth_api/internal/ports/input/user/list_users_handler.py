from typing import Protocol

from auth_api.internal.core.domain.models.user.user import User


class ListUsersHandlerProtocol(Protocol):
    async def handle(self) -> list[User]:
        ...
