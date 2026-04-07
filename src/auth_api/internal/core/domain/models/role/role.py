import uuid

from auth_api.internal.pkg.domain import BaseAggregate
from auth_api.internal.core.domain.models.role.errors import (
    RoleNameTooShortError,
    RoleNameTooLongError,
)
from auth_api.internal.pkg.errors import ParamEmptyError

ADMIN_ROLE_NAME = "admin"

ROLE_NAME_MIN_LENGTH = 3
ROLE_NAME_MAX_LENGTH = 10


class Role(BaseAggregate[uuid.UUID]):
    def __init__(self,
                 oid: uuid.UUID,
                 name: str) -> None:
        if not name:
            raise ParamEmptyError(param='name')
        if len(name) < ROLE_NAME_MIN_LENGTH:
            raise RoleNameTooShortError(min_length=ROLE_NAME_MIN_LENGTH)
        if len(name) > ROLE_NAME_MAX_LENGTH:
            raise RoleNameTooLongError(max_length=ROLE_NAME_MAX_LENGTH)
        super().__init__(oid)
        self.name = name

