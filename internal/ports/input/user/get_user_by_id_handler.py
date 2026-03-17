import uuid
from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.user.user import User


@dataclass(kw_only=True)
class GetUserById:
    user_id: uuid.UUID


class GetUserByIdHandlerProtocol(Protocol):
    async def handle(self, query: GetUserById) -> User:
        ...
