import uuid
from dataclasses import dataclass
from typing import Protocol

from auth_api.internal.ports.input.user.login_user_handler import LoggedInUser
from auth_api.internal.ports.output.token_provider import UserTokenData


@dataclass(kw_only=True)
class RefreshSession:
    user: UserTokenData
    jti: uuid.UUID
    device_fingerprint: str


class RefreshSessionHandlerProtocol(Protocol):
    async def handle(self, command: RefreshSession) -> LoggedInUser:
        ...

