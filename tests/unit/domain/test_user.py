import uuid
from collections.abc import Callable

import pytest

from auth_api.internal.core.domain.models.user.user import (
    User,
    USER_FIRST_NAME_MAX_LENGTH,
    USER_LAST_NAME_MAX_LENGTH,
)
from auth_api.internal.core.domain.models.user.errors import (
    UserFirstNameTooLongError,
    UserLastNameTooLongError,
)
from auth_api.internal.pkg.errors import ParamEmptyError


class TestUserCreation:
    """РўРµСЃС‚С‹ СЃРѕР·РґР°РЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ СЃ РєРѕСЂСЂРµРєС‚РЅС‹РјРё РґР°РЅРЅС‹РјРё."""

    def test_create_valid_user(self, user_factory: Callable[..., User]):
        """РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ СЃРѕР·РґР°С‘С‚СЃСЏ СЃ РєРѕСЂСЂРµРєС‚РЅС‹РјРё РїРѕР»СЏРјРё."""
        uid = uuid.uuid4()
        user = user_factory(oid=uid, login="alice", first_name="Alice",
                            last_name="Smith")

        assert user.id == uid
        assert user.login == "alice"
        assert user.first_name == "Alice"
        assert user.last_name == "Smith"
        assert user.is_superuser is False
        assert user.is_active is True

    def test_create_superuser(self, user_factory: Callable[..., User]):
        """РЎСѓРїРµСЂРїРѕР»СЊР·РѕРІР°С‚РµР»СЊ СЃРѕР·РґР°С‘С‚СЃСЏ СЃ С„Р»Р°РіРѕРј is_superuser=True."""
        user = user_factory(is_superuser=True)
        assert user.is_superuser is True

    def test_roles_default_to_empty_list(self, user_factory: Callable[..., User]):
        """Р•СЃР»Рё СЂРѕР»Рё РЅРµ СѓРєР°Р·Р°РЅС‹, РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ РїСѓСЃС‚РѕР№ СЃРїРёСЃРѕРє."""
        user = user_factory(roles=None)
        assert user.roles == []

    def test_roles_assigned(self, user_factory: Callable[..., User]):
        """РЎРїРёСЃРѕРє СЂРѕР»РµР№ СЃРѕС…СЂР°РЅСЏРµС‚СЃСЏ РєРѕСЂСЂРµРєС‚РЅРѕ."""
        user = user_factory(roles=["admin", "subscriber"])
        assert user.roles == ["admin", "subscriber"]


class TestUserValidation:
    """РўРµСЃС‚С‹ РІР°Р»РёРґР°С†РёРё РїРѕР»РµР№ РїСЂРё СЃРѕР·РґР°РЅРёРё User."""

    def test_empty_login_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """РџСѓСЃС‚РѕР№ Р»РѕРіРёРЅ РІС‹Р·С‹РІР°РµС‚ ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="login"):
            user_factory(login="")

    def test_empty_password_hash_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """РџСѓСЃС‚РѕР№ С…СЌС€ РїР°СЂРѕР»СЏ РІС‹Р·С‹РІР°РµС‚ ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="password_hash"):
            user_factory(password_hash="")

    def test_empty_first_name_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """РџСѓСЃС‚РѕРµ РёРјСЏ РІС‹Р·С‹РІР°РµС‚ ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="first_name"):
            user_factory(first_name="")

    def test_empty_last_name_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """РџСѓСЃС‚Р°СЏ С„Р°РјРёР»РёСЏ РІС‹Р·С‹РІР°РµС‚ ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="last_name"):
            user_factory(last_name="")

    def test_first_name_too_long_raises_error(self, user_factory: Callable[..., User]):
        """РРјСЏ РґР»РёРЅРЅРµРµ РјР°РєСЃРёРјСѓРјР° РІС‹Р·С‹РІР°РµС‚ UserFirstNameTooLongError."""
        long_name = "A" * (USER_FIRST_NAME_MAX_LENGTH + 1)
        with pytest.raises(UserFirstNameTooLongError):
            user_factory(first_name=long_name)

    def test_first_name_at_max_length_accepted(self, user_factory: Callable[..., User]):
        """РРјСЏ СЂРѕРІРЅРѕ РЅР° РјР°РєСЃРёРјСѓРјРµ РґР»РёРЅС‹ РїСЂРѕС…РѕРґРёС‚ РІР°Р»РёРґР°С†РёСЋ."""
        max_name = "A" * USER_FIRST_NAME_MAX_LENGTH
        user = user_factory(first_name=max_name)
        assert user.first_name == max_name

    def test_last_name_too_long_raises_error(self, user_factory: Callable[..., User]):
        """Р¤Р°РјРёР»РёСЏ РґР»РёРЅРЅРµРµ РјР°РєСЃРёРјСѓРјР° РІС‹Р·С‹РІР°РµС‚ UserLastNameTooLongError."""
        long_name = "B" * (USER_LAST_NAME_MAX_LENGTH + 1)
        with pytest.raises(UserLastNameTooLongError):
            user_factory(last_name=long_name)

    def test_last_name_at_max_length_accepted(self, user_factory: Callable[..., User]):
        """Р¤Р°РјРёР»РёСЏ СЂРѕРІРЅРѕ РЅР° РјР°РєСЃРёРјСѓРјРµ РґР»РёРЅС‹ РїСЂРѕС…РѕРґРёС‚ РІР°Р»РёРґР°С†РёСЋ."""
        max_name = "B" * USER_LAST_NAME_MAX_LENGTH
        user = user_factory(last_name=max_name)
        assert user.last_name == max_name

    def test_none_oid_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """None РІ РєР°С‡РµСЃС‚РІРµ domain_id РІС‹Р·С‹РІР°РµС‚ ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="domain_id"):
            user_factory(oid=None)


class TestUserIdentity:
    """РўРµСЃС‚С‹ СЂР°РІРµРЅСЃС‚РІР° Рё С…РµС€РёСЂРѕРІР°РЅРёСЏ РїРѕ identity (id)."""

    def test_users_with_same_id_are_equal(self, user_factory: Callable[..., User]):
        """Р”РІР° User СЃ РѕРґРёРЅР°РєРѕРІС‹Рј id СЃС‡РёС‚Р°СЋС‚СЃСЏ СЂР°РІРЅС‹РјРё."""
        uid = uuid.uuid4()
        user1 = user_factory(oid=uid, login="alice")
        user2 = user_factory(oid=uid, login="bob")
        assert user1 == user2

    def test_users_with_different_id_are_not_equal(self, user_factory: Callable[..., User]):
        """Р”РІР° User СЃ СЂР°Р·РЅС‹РјРё id РЅРµ СЂР°РІРЅС‹."""
        user1 = user_factory(oid=uuid.uuid4())
        user2 = user_factory(oid=uuid.uuid4())
        assert user1 != user2

    def test_user_hash_depends_on_id(self, user_factory: Callable[..., User]):
        """РҐСЌС€ User Р·Р°РІРёСЃРёС‚ С‚РѕР»СЊРєРѕ РѕС‚ id."""
        uid = uuid.uuid4()
        user1 = user_factory(oid=uid)
        user2 = user_factory(oid=uid)
        assert hash(user1) == hash(user2)

    def test_user_not_equal_to_non_entity(self, user_factory: Callable[..., User]):
        """User РЅРµ СЂР°РІРµРЅ РѕР±СЉРµРєС‚Сѓ РґСЂСѓРіРѕРіРѕ С‚РёРїР°."""
        user = user_factory()
        assert user != "not_a_user"


class TestUserDomainEvents:
    """РўРµСЃС‚С‹ РјРµС…Р°РЅРёР·РјР° РґРѕРјРµРЅРЅС‹С… СЃРѕР±С‹С‚РёР№, СѓРЅР°СЃР»РµРґРѕРІР°РЅРЅРѕРіРѕ РѕС‚ BaseAggregate."""

    def test_domain_events_initially_empty(self, user_factory: Callable[..., User]):
        """РЈ РЅРѕРІРѕРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РЅРµС‚ РґРѕРјРµРЅРЅС‹С… СЃРѕР±С‹С‚РёР№."""
        user = user_factory()
        assert user.domain_events == []

    def test_raise_and_clear_domain_events(self, user_factory: Callable[..., User]):
        """РњРѕР¶РЅРѕ РґРѕР±Р°РІРёС‚СЊ Рё РѕС‡РёСЃС‚РёС‚СЊ РґРѕРјРµРЅРЅС‹Рµ СЃРѕР±С‹С‚РёСЏ."""
        user = user_factory()

        class FakeEvent:
            pass

        event = FakeEvent()
        user.raise_domain_event(event)
        assert len(user.domain_events) == 1
        assert user.domain_events[0] is event

        user.clear_domain_events()
        assert user.domain_events == []

