from dataclasses import dataclass
from typing import Protocol
import uuid


@dataclass(kw_only=True)
class LogoutAll:
    login: str
    access_token_jti: uuid.UUID


class LogoutAllHandlerProtocol(Protocol):
    async def handle(self, command: LogoutAll) -> None:
        ...
