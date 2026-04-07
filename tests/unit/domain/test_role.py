import uuid
from collections.abc import Callable

import pytest

from auth_api.internal.core.domain.models.role.role import (
    Role,
    ROLE_NAME_MIN_LENGTH,
    ROLE_NAME_MAX_LENGTH,
    ADMIN_ROLE_NAME,
)
from auth_api.internal.core.domain.models.role.errors import (
    RoleNameTooShortError,
    RoleNameTooLongError,
)
from auth_api.internal.pkg.errors import ParamEmptyError


class TestRoleCreation:
    """Role creation tests with valid input."""

    def test_create_valid_role(self, role_factory: Callable[..., Role]):
        """Role is created with valid name."""
        rid = uuid.uuid4()
        role = role_factory(oid=rid, name=ADMIN_ROLE_NAME)
        assert role.id == rid
        assert role.name == ADMIN_ROLE_NAME

    def test_admin_role_name_constant(self):
        """ADMIN_ROLE_NAME constant equals 'admin'."""
        assert ADMIN_ROLE_NAME == "admin"


class TestRoleNameValidation:
    """Role name length validation tests."""

    def test_empty_name_raises_param_empty_error(
            self, role_factory: Callable[..., Role]):
        """Empty name raises ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="name"):
            role_factory(name="")

    def test_name_too_short_raises_error(
            self, role_factory: Callable[..., Role]):
        """Name shorter than minimum raises RoleNameTooShortError."""
        short_name = "a" * (ROLE_NAME_MIN_LENGTH - 1)
        with pytest.raises(RoleNameTooShortError):
            role_factory(name=short_name)

    def test_name_at_min_length_accepted(
            self, role_factory: Callable[..., Role]):
        """Name at minimum length is accepted."""
        min_name = "a" * ROLE_NAME_MIN_LENGTH
        role = role_factory(name=min_name)
        assert role.name == min_name

    def test_name_too_long_raises_error(
            self, role_factory: Callable[..., Role]):
        """Name longer than maximum raises RoleNameTooLongError."""
        long_name = "a" * (ROLE_NAME_MAX_LENGTH + 1)
        with pytest.raises(RoleNameTooLongError):
            role_factory(name=long_name)

    def test_name_at_max_length_accepted(
            self, role_factory: Callable[..., Role]):
        """Name at maximum length is accepted."""
        max_name = "a" * ROLE_NAME_MAX_LENGTH
        role = role_factory(name=max_name)
        assert role.name == max_name

    def test_none_oid_raises_param_empty_error(
            self, role_factory: Callable[..., Role]):
        """None domain_id raises ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="domain_id"):
            role_factory(oid=None)


class TestRoleIdentity:
    """Identity-based equality and hashing tests."""

    def test_roles_with_same_id_are_equal(
            self, role_factory: Callable[..., Role]):
        """Roles with same id are equal."""
        rid = uuid.uuid4()
        role1 = role_factory(oid=rid, name="editor")
        role2 = role_factory(oid=rid, name="viewer")
        assert role1 == role2

    def test_roles_with_different_id_are_not_equal(
            self, role_factory: Callable[..., Role]):
        """Roles with different id are not equal."""
        role1 = role_factory(oid=uuid.uuid4())
        role2 = role_factory(oid=uuid.uuid4())
        assert role1 != role2

    def test_role_hash_depends_on_id(
            self, role_factory: Callable[..., Role]):
        """Role hash depends only on id."""
        rid = uuid.uuid4()
        role1 = role_factory(oid=rid)
        role2 = role_factory(oid=rid)
        assert hash(role1) == hash(role2)


class TestRoleErrorMessages:
    """Validation error message tests."""

    def test_too_short_error_message(self):
        """RoleNameTooShortError contains expected message."""
        err = RoleNameTooShortError(min_length=3)
        assert "at least 3 characters" in err.get_message()

    def test_too_long_error_message(self):
        """RoleNameTooLongError contains expected message."""
        err = RoleNameTooLongError(max_length=10)
        assert "at most 10 characters" in err.get_message()

    def test_too_short_error_to_dict(self):
        """RoleNameTooShortError is serialized to dict."""
        err = RoleNameTooShortError(min_length=3)
        d = err.to_dict()
        assert d["code"] == "ROLE_NAME_TOO_SHORT"
        assert "message" in d

    def test_too_long_error_to_dict(self):
        """RoleNameTooLongError is serialized to dict."""
        err = RoleNameTooLongError(max_length=10)
        d = err.to_dict()
        assert d["code"] == "ROLE_NAME_TOO_LONG"
        assert "message" in d
