from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.user.user import User


@dataclass(kw_only=True)
class CreateUser:
    login: str
    password: str
    first_name: str
    last_name: str
    is_superuser: bool = False
    is_active: bool = False


class CreateUserHandlerProtocol(Protocol):
    async def handle(self, command: CreateUser) -> User:
        ...
