import datetime
import uuid

from internal.pkg.domain import BaseAggregate
from internal.pkg.errors import ParamEmptyError
from internal.core.domain.models.user.errors import (
    UserLastNameTooLongError, UserFirstNameTooLongError,
)

USER_FIRST_NAME_MAX_LENGTH = 255
USER_LAST_NAME_MAX_LENGTH = 255


class User(BaseAggregate[uuid.UUID]):
    def __init__(self,
                 oid: uuid.UUID,
                 login: str,
                 password_hash: str,
                 first_name: str,
                 last_name: str,
                 roles: list[str] | None = None,
                 is_superuser: bool = False,
                 is_active: bool = False,
                 created_at: datetime.datetime =
                 datetime.datetime.now(datetime.timezone.utc)):
        if not login:
            raise ParamEmptyError(param='login')
        if not password_hash:
            raise ParamEmptyError(param='password_hash')
        if not first_name:
            raise ParamEmptyError(param='first_name')
        if len(first_name) > USER_FIRST_NAME_MAX_LENGTH:
            raise UserFirstNameTooLongError(
                max_length=USER_FIRST_NAME_MAX_LENGTH)
        if not last_name:
            raise ParamEmptyError(param='last_name')
        if len(last_name) > USER_LAST_NAME_MAX_LENGTH:
            raise UserLastNameTooLongError(
                max_length=USER_LAST_NAME_MAX_LENGTH)
        super().__init__(oid)
        self.login = login
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.roles = roles or []
        self.created_at = created_at
        self.is_superuser = is_superuser
        self.is_active = is_active
