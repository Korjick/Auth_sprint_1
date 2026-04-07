import uuid
from dataclasses import dataclass
from typing import Protocol

from auth_api.internal.core.domain.models.user.user import User


@dataclass(kw_only=True)
class UpdateUser:
    user_id: uuid.UUID
    current_password: str
    new_login: str
    new_password: str


class UpdateUserHandlerProtocol(Protocol):
    async def handle(self, command: UpdateUser) -> User:
        ...

