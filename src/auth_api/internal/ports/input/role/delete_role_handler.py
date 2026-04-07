import uuid
from dataclasses import dataclass
from typing import Protocol


@dataclass(kw_only=True)
class DeleteRole:
    role_id: uuid.UUID


class DeleteRoleHandlerProtocol(Protocol):
    async def handle(self, command: DeleteRole) -> None:
        ...
