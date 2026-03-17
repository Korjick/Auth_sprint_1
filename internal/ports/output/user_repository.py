import uuid
from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.user.user import User


@dataclass(kw_only=True)
class UserCreate:
    login: str
    password_hash: str
    first_name: str
    last_name: str
    is_superuser: bool = False
    is_active: bool = False


class UserRepository(Protocol):
    async def save_user(self, user_to_create: UserCreate) -> User:
        pass

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        pass

    async def get_user_by_login(self, login: str) -> User:
        pass

    async def update_login(self, user_id: uuid.UUID, new_login: str) -> User:
        pass

    async def update_password(self, user_id: uuid.UUID,
                              new_password_hash: str) -> User:
        pass

    async def add_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> User:
        pass

    async def remove_role(self, user_id: uuid.UUID,
                          role_id: uuid.UUID) -> User:
        pass
