import uuid
from dataclasses import dataclass
from typing import Protocol

from auth_api.internal.core.domain.models.user.user import User


@dataclass(kw_only=True)
class AssignRole:
    user_id: uuid.UUID
    role_id: uuid.UUID


class AssignRoleHandlerProtocol(Protocol):
    async def handle(self, command: AssignRole) -> User:
        ...

