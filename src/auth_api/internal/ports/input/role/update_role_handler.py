import uuid
from dataclasses import dataclass
from typing import Protocol

from auth_api.internal.core.domain.models.role.role import Role


@dataclass(kw_only=True)
class UpdateRole:
    role_id: uuid.UUID
    name: str


class UpdateRoleHandlerProtocol(Protocol):
    async def handle(self, command: UpdateRole) -> Role:
        ...

