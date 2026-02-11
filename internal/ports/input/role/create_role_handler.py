from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.role.role import Role


@dataclass(kw_only=True)
class CreateRole:
    name: str


class CreateRoleHandlerProtocol(Protocol):
    async def handle(self, command: CreateRole) -> Role:
        ...
