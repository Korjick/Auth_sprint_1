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
    """РўРµСЃС‚С‹ СЃРѕР·РґР°РЅРёСЏ СЂРѕР»Рё СЃ РєРѕСЂСЂРµРєС‚РЅС‹РјРё РґР°РЅРЅС‹РјРё."""

    def test_create_valid_role(self, role_factory: Callable[..., Role]):
        """Р РѕР»СЊ СЃРѕР·РґР°С‘С‚СЃСЏ СЃ РєРѕСЂСЂРµРєС‚РЅС‹Рј РёРјРµРЅРµРј."""
        rid = uuid.uuid4()
        role = role_factory(oid=rid, name=ADMIN_ROLE_NAME)
        assert role.id == rid
        assert role.name == ADMIN_ROLE_NAME

    def test_admin_role_name_constant(self):
        """РљРѕРЅСЃС‚Р°РЅС‚Р° ADMIN_ROLE_NAME СЂР°РІРЅР° 'admin'."""
        assert ADMIN_ROLE_NAME == "admin"


class TestRoleNameValidation:
    """РўРµСЃС‚С‹ РІР°Р»РёРґР°С†РёРё РґР»РёРЅС‹ РёРјРµРЅРё СЂРѕР»Рё."""

    def test_empty_name_raises_param_empty_error(self, role_factory: Callable[..., Role]):
        """РџСѓСЃС‚РѕРµ РёРјСЏ РІС‹Р·С‹РІР°РµС‚ ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="name"):
            role_factory(name="")

    def test_name_too_short_raises_error(self, role_factory: Callable[..., Role]):
        """РРјСЏ РєРѕСЂРѕС‡Рµ РјРёРЅРёРјСѓРјР° РІС‹Р·С‹РІР°РµС‚ RoleNameTooShortError."""
        short_name = "a" * (ROLE_NAME_MIN_LENGTH - 1)
        with pytest.raises(RoleNameTooShortError):
            role_factory(name=short_name)

    def test_name_at_min_length_accepted(self, role_factory: Callable[..., Role]):
        """РРјСЏ СЂРѕРІРЅРѕ РЅР° РјРёРЅРёРјСѓРјРµ РґР»РёРЅС‹ РїСЂРѕС…РѕРґРёС‚ РІР°Р»РёРґР°С†РёСЋ."""
        min_name = "a" * ROLE_NAME_MIN_LENGTH
        role = role_factory(name=min_name)
        assert role.name == min_name

    def test_name_too_long_raises_error(self, role_factory: Callable[..., Role]):
        """РРјСЏ РґР»РёРЅРЅРµРµ РјР°РєСЃРёРјСѓРјР° РІС‹Р·С‹РІР°РµС‚ RoleNameTooLongError."""
        long_name = "a" * (ROLE_NAME_MAX_LENGTH + 1)
        with pytest.raises(RoleNameTooLongError):
            role_factory(name=long_name)

    def test_name_at_max_length_accepted(self, role_factory: Callable[..., Role]):
        """РРјСЏ СЂРѕРІРЅРѕ РЅР° РјР°РєСЃРёРјСѓРјРµ РґР»РёРЅС‹ РїСЂРѕС…РѕРґРёС‚ РІР°Р»РёРґР°С†РёСЋ."""
        max_name = "a" * ROLE_NAME_MAX_LENGTH
        role = role_factory(name=max_name)
        assert role.name == max_name

    def test_none_oid_raises_param_empty_error(self, role_factory: Callable[..., Role]):
        """None РІ РєР°С‡РµСЃС‚РІРµ domain_id РІС‹Р·С‹РІР°РµС‚ ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="domain_id"):
            role_factory(oid=None)


class TestRoleIdentity:
    """РўРµСЃС‚С‹ СЂР°РІРµРЅСЃС‚РІР° Рё С…РµС€РёСЂРѕРІР°РЅРёСЏ РїРѕ identity."""

    def test_roles_with_same_id_are_equal(self, role_factory: Callable[..., Role]):
        """Р”РІРµ СЂРѕР»Рё СЃ РѕРґРёРЅР°РєРѕРІС‹Рј id СЃС‡РёС‚Р°СЋС‚СЃСЏ СЂР°РІРЅС‹РјРё."""
        rid = uuid.uuid4()
        role1 = role_factory(oid=rid, name="editor")
        role2 = role_factory(oid=rid, name="viewer")
        assert role1 == role2

    def test_roles_with_different_id_are_not_equal(self, role_factory: Callable[..., Role]):
        """Р”РІРµ СЂРѕР»Рё СЃ СЂР°Р·РЅС‹РјРё id РЅРµ СЂР°РІРЅС‹."""
        role1 = role_factory(oid=uuid.uuid4())
        role2 = role_factory(oid=uuid.uuid4())
        assert role1 != role2

    def test_role_hash_depends_on_id(self, role_factory: Callable[..., Role]):
        """РҐСЌС€ Role Р·Р°РІРёСЃРёС‚ С‚РѕР»СЊРєРѕ РѕС‚ id."""
        rid = uuid.uuid4()
        role1 = role_factory(oid=rid)
        role2 = role_factory(oid=rid)
        assert hash(role1) == hash(role2)


class TestRoleErrorMessages:
    """РўРµСЃС‚С‹ СЃРѕРѕР±С‰РµРЅРёР№ РѕС€РёР±РѕРє РІР°Р»РёРґР°С†РёРё."""

    def test_too_short_error_message(self):
        """RoleNameTooShortError СЃРѕРґРµСЂР¶РёС‚ РєРѕСЂСЂРµРєС‚РЅРѕРµ СЃРѕРѕР±С‰РµРЅРёРµ."""
        err = RoleNameTooShortError(min_length=3)
        assert "at least 3 characters" in err.get_message()

    def test_too_long_error_message(self):
        """RoleNameTooLongError СЃРѕРґРµСЂР¶РёС‚ РєРѕСЂСЂРµРєС‚РЅРѕРµ СЃРѕРѕР±С‰РµРЅРёРµ."""
        err = RoleNameTooLongError(max_length=10)
        assert "at most 10 characters" in err.get_message()

    def test_too_short_error_to_dict(self):
        """RoleNameTooShortError СЃРµСЂРёР°Р»РёР·СѓРµС‚СЃСЏ РІ dict."""
        err = RoleNameTooShortError(min_length=3)
        d = err.to_dict()
        assert d["code"] == "ROLE_NAME_TOO_SHORT"
        assert "message" in d

    def test_too_long_error_to_dict(self):
        """RoleNameTooLongError СЃРµСЂРёР°Р»РёР·СѓРµС‚СЃСЏ РІ dict."""
        err = RoleNameTooLongError(max_length=10)
        d = err.to_dict()
        assert d["code"] == "ROLE_NAME_TOO_LONG"
        assert "message" in d

