from dataclasses import dataclass
from typing import Protocol

from auth_api.internal.core.domain.models.user.user import User


@dataclass(kw_only=True)
class GetUserByLogin:
    login: str


class GetUserByLoginHandlerProtocol(Protocol):
    async def handle(self, query: GetUserByLogin) -> User:
        ...

