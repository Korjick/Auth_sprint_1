import uuid
from dataclasses import dataclass
from typing import Protocol


@dataclass(kw_only=True)
class Logout:
    login: str
    device_fingerprint: str
    access_token_jti: uuid.UUID


class LogoutHandlerProtocol(Protocol):
    async def handle(self, command: Logout) -> None:
        ...
