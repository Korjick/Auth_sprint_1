from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.role.role import Role


@dataclass(kw_only=True)
class ListRoles:
    pass


class ListRolesHandlerProtocol(Protocol):
    async def handle(self, query: ListRoles) -> list[Role]:
        ...
