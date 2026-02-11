from dataclasses import dataclass
from typing import Protocol


@dataclass(kw_only=True)
class LoginUser:
    login: str
    password: str
    device_fingerprint: str


@dataclass(kw_only=True)
class LoggedInUser:
    access_session: str
    refresh_session: str


class LoginUserHandlerProtocol(Protocol):
    async def handle(self, command: LoginUser) -> LoggedInUser:
        ...
