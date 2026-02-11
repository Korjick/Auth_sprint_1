import uuid

import pytest

from internal.core.domain.models.role.role import (
    Role,
    ROLE_NAME_MIN_LENGTH,
    ROLE_NAME_MAX_LENGTH,
    ADMIN_ROLE_NAME,
)
from internal.core.domain.models.role.errors import (
    RoleNameTooShortError,
    RoleNameTooLongError,
)
from internal.pkg.errors import ParamEmptyError


def _make_role(**overrides) -> Role:
    """Фабрика для создания Role с валидными значениями по умолчанию."""
    defaults = dict(
        oid=uuid.uuid4(),
        name=ADMIN_ROLE_NAME,
    )
    defaults.update(overrides)
    return Role(**defaults)


class TestRoleCreation:
    """Тесты создания роли с корректными данными."""

    def test_create_valid_role(self):
        """Роль создаётся с корректным именем."""
        rid = uuid.uuid4()
        role = _make_role(oid=rid, name=ADMIN_ROLE_NAME)
        assert role.id == rid
        assert role.name == ADMIN_ROLE_NAME

    def test_admin_role_name_constant(self):
        """Константа ADMIN_ROLE_NAME равна 'admin'."""
        assert ADMIN_ROLE_NAME == "admin"


class TestRoleNameValidation:
    """Тесты валидации длины имени роли."""

    def test_empty_name_raises_param_empty_error(self):
        """Пустое имя вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="name"):
            _make_role(name="")

    def test_name_too_short_raises_error(self):
        """Имя короче минимума вызывает RoleNameTooShortError."""
        short_name = "a" * (ROLE_NAME_MIN_LENGTH - 1)
        with pytest.raises(RoleNameTooShortError):
            _make_role(name=short_name)

    def test_name_at_min_length_accepted(self):
        """Имя ровно на минимуме длины проходит валидацию."""
        min_name = "a" * ROLE_NAME_MIN_LENGTH
        role = _make_role(name=min_name)
        assert role.name == min_name

    def test_name_too_long_raises_error(self):
        """Имя длиннее максимума вызывает RoleNameTooLongError."""
        long_name = "a" * (ROLE_NAME_MAX_LENGTH + 1)
        with pytest.raises(RoleNameTooLongError):
            _make_role(name=long_name)

    def test_name_at_max_length_accepted(self):
        """Имя ровно на максимуме длины проходит валидацию."""
        max_name = "a" * ROLE_NAME_MAX_LENGTH
        role = _make_role(name=max_name)
        assert role.name == max_name

    def test_none_oid_raises_param_empty_error(self):
        """None в качестве domain_id вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="domain_id"):
            _make_role(oid=None)


class TestRoleIdentity:
    """Тесты равенства и хеширования по identity."""

    def test_roles_with_same_id_are_equal(self):
        """Две роли с одинаковым id считаются равными."""
        rid = uuid.uuid4()
        role1 = _make_role(oid=rid, name="editor")
        role2 = _make_role(oid=rid, name="viewer")
        assert role1 == role2

    def test_roles_with_different_id_are_not_equal(self):
        """Две роли с разными id не равны."""
        role1 = _make_role(oid=uuid.uuid4())
        role2 = _make_role(oid=uuid.uuid4())
        assert role1 != role2

    def test_role_hash_depends_on_id(self):
        """Хэш Role зависит только от id."""
        rid = uuid.uuid4()
        role1 = _make_role(oid=rid)
        role2 = _make_role(oid=rid)
        assert hash(role1) == hash(role2)


class TestRoleErrorMessages:
    """Тесты сообщений ошибок валидации."""

    def test_too_short_error_message(self):
        """RoleNameTooShortError содержит корректное сообщение."""
        err = RoleNameTooShortError(min_length=3)
        assert "at least 3 characters" in err.get_message()

    def test_too_long_error_message(self):
        """RoleNameTooLongError содержит корректное сообщение."""
        err = RoleNameTooLongError(max_length=10)
        assert "at most 10 characters" in err.get_message()

    def test_too_short_error_to_dict(self):
        """RoleNameTooShortError сериализуется в dict."""
        err = RoleNameTooShortError(min_length=3)
        d = err.to_dict()
        assert d["code"] == "ROLE_NAME_TOO_SHORT"
        assert "message" in d

    def test_too_long_error_to_dict(self):
        """RoleNameTooLongError сериализуется в dict."""
        err = RoleNameTooLongError(max_length=10)
        d = err.to_dict()
        assert d["code"] == "ROLE_NAME_TOO_LONG"
        assert "message" in d
