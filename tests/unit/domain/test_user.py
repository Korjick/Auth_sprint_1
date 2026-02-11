import uuid
import datetime

import pytest

from internal.core.domain.models.user.user import (
    User,
    USER_FIRST_NAME_MAX_LENGTH,
    USER_LAST_NAME_MAX_LENGTH,
)
from internal.core.domain.models.user.errors import (
    UserFirstNameTooLongError,
    UserLastNameTooLongError,
)
from internal.pkg.errors import ParamEmptyError


def _make_user(**overrides) -> User:
    """Фабрика для создания User с валидными значениями по умолчанию."""
    defaults = dict(
        oid=uuid.uuid4(),
        login="john_doe",
        password_hash="hashed_password_123",
        first_name="John",
        last_name="Doe",
        roles=["subscriber"],
        is_superuser=False,
        is_active=True,
        created_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
    )
    defaults.update(overrides)
    return User(**defaults)


class TestUserCreation:
    """Тесты создания пользователя с корректными данными."""

    def test_create_valid_user(self):
        """Пользователь создаётся с корректными полями."""
        uid = uuid.uuid4()
        user = _make_user(oid=uid, login="alice", first_name="Alice",
                          last_name="Smith")

        assert user.id == uid
        assert user.login == "alice"
        assert user.first_name == "Alice"
        assert user.last_name == "Smith"
        assert user.is_superuser is False
        assert user.is_active is True

    def test_create_superuser(self):
        """Суперпользователь создаётся с флагом is_superuser=True."""
        user = _make_user(is_superuser=True)
        assert user.is_superuser is True

    def test_roles_default_to_empty_list(self):
        """Если роли не указаны, используется пустой список."""
        user = _make_user(roles=None)
        assert user.roles == []

    def test_roles_assigned(self):
        """Список ролей сохраняется корректно."""
        user = _make_user(roles=["admin", "subscriber"])
        assert user.roles == ["admin", "subscriber"]


class TestUserValidation:
    """Тесты валидации полей при создании User."""

    def test_empty_login_raises_param_empty_error(self):
        """Пустой логин вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="login"):
            _make_user(login="")

    def test_empty_password_hash_raises_param_empty_error(self):
        """Пустой хэш пароля вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="password_hash"):
            _make_user(password_hash="")

    def test_empty_first_name_raises_param_empty_error(self):
        """Пустое имя вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="first_name"):
            _make_user(first_name="")

    def test_empty_last_name_raises_param_empty_error(self):
        """Пустая фамилия вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="last_name"):
            _make_user(last_name="")

    def test_first_name_too_long_raises_error(self):
        """Имя длиннее максимума вызывает UserFirstNameTooLongError."""
        long_name = "A" * (USER_FIRST_NAME_MAX_LENGTH + 1)
        with pytest.raises(UserFirstNameTooLongError):
            _make_user(first_name=long_name)

    def test_first_name_at_max_length_accepted(self):
        """Имя ровно на максимуме длины проходит валидацию."""
        max_name = "A" * USER_FIRST_NAME_MAX_LENGTH
        user = _make_user(first_name=max_name)
        assert user.first_name == max_name

    def test_last_name_too_long_raises_error(self):
        """Фамилия длиннее максимума вызывает UserLastNameTooLongError."""
        long_name = "B" * (USER_LAST_NAME_MAX_LENGTH + 1)
        with pytest.raises(UserLastNameTooLongError):
            _make_user(last_name=long_name)

    def test_last_name_at_max_length_accepted(self):
        """Фамилия ровно на максимуме длины проходит валидацию."""
        max_name = "B" * USER_LAST_NAME_MAX_LENGTH
        user = _make_user(last_name=max_name)
        assert user.last_name == max_name

    def test_none_oid_raises_param_empty_error(self):
        """None в качестве domain_id вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="domain_id"):
            _make_user(oid=None)


class TestUserIdentity:
    """Тесты равенства и хеширования по identity (id)."""

    def test_users_with_same_id_are_equal(self):
        """Два User с одинаковым id считаются равными."""
        uid = uuid.uuid4()
        user1 = _make_user(oid=uid, login="alice")
        user2 = _make_user(oid=uid, login="bob")
        assert user1 == user2

    def test_users_with_different_id_are_not_equal(self):
        """Два User с разными id не равны."""
        user1 = _make_user(oid=uuid.uuid4())
        user2 = _make_user(oid=uuid.uuid4())
        assert user1 != user2

    def test_user_hash_depends_on_id(self):
        """Хэш User зависит только от id."""
        uid = uuid.uuid4()
        user1 = _make_user(oid=uid)
        user2 = _make_user(oid=uid)
        assert hash(user1) == hash(user2)

    def test_user_not_equal_to_non_entity(self):
        """User не равен объекту другого типа."""
        user = _make_user()
        assert user != "not_a_user"


class TestUserDomainEvents:
    """Тесты механизма доменных событий, унаследованного от BaseAggregate."""

    def test_domain_events_initially_empty(self):
        """У нового пользователя нет доменных событий."""
        user = _make_user()
        assert user.domain_events == []

    def test_raise_and_clear_domain_events(self):
        """Можно добавить и очистить доменные события."""
        user = _make_user()

        class FakeEvent:
            pass

        event = FakeEvent()
        user.raise_domain_event(event)
        assert len(user.domain_events) == 1
        assert user.domain_events[0] is event

        user.clear_domain_events()
        assert user.domain_events == []
