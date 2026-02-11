import uuid
from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.role.role import Role


@dataclass(kw_only=True)
class RoleCreate:
    name: str


class RoleRepository(Protocol):
    async def create_role(self, role_create: RoleCreate) -> Role:
        ...

    async def update_role(self, role_id: uuid.UUID, name: str) -> Role:
        ...

    async def delete_role(self, role_id: uuid.UUID) -> None:
        ...

    async def get_role_by_id(self, role_id: uuid.UUID) -> Role:
        ...

    async def list_roles(self) -> list[Role]:
        ...
