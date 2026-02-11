import uuid
from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.role.role import Role


@dataclass(kw_only=True)
class UpdateRole:
    role_id: uuid.UUID
    name: str


class UpdateRoleHandlerProtocol(Protocol):
    async def handle(self, command: UpdateRole) -> Role:
        ...
