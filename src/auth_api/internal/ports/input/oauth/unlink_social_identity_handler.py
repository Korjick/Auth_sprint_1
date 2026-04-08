import uuid
from dataclasses import dataclass
from typing import Protocol


@dataclass(kw_only=True)
class UnlinkSocialIdentity:
    user_id: uuid.UUID
    provider: str


class UnlinkSocialIdentityHandlerProtocol(Protocol):
    async def handle(self, command: UnlinkSocialIdentity) -> None:
        ...
