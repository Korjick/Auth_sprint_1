import uuid
from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.user.user import User


@dataclass(kw_only=True)
class RemoveRole:
    user_id: uuid.UUID
    role_id: uuid.UUID


class RemoveRoleHandlerProtocol(Protocol):
    async def handle(self, command: RemoveRole) -> User:
        ...
