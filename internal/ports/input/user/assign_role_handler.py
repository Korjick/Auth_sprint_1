import uuid
from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.user.user import User


@dataclass(kw_only=True)
class AssignRole:
    user_login: str
    role_id: uuid.UUID


class AssignRoleHandlerProtocol(Protocol):
    async def handle(self, command: AssignRole) -> User:
        ...
