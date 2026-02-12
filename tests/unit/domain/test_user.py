import uuid
from collections.abc import Callable

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


class TestUserCreation:
    """Тесты создания пользователя с корректными данными."""

    def test_create_valid_user(self, user_factory: Callable[..., User]):
        """Пользователь создаётся с корректными полями."""
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
        """Суперпользователь создаётся с флагом is_superuser=True."""
        user = user_factory(is_superuser=True)
        assert user.is_superuser is True

    def test_roles_default_to_empty_list(self, user_factory: Callable[..., User]):
        """Если роли не указаны, используется пустой список."""
        user = user_factory(roles=None)
        assert user.roles == []

    def test_roles_assigned(self, user_factory: Callable[..., User]):
        """Список ролей сохраняется корректно."""
        user = user_factory(roles=["admin", "subscriber"])
        assert user.roles == ["admin", "subscriber"]


class TestUserValidation:
    """Тесты валидации полей при создании User."""

    def test_empty_login_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """Пустой логин вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="login"):
            user_factory(login="")

    def test_empty_password_hash_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """Пустой хэш пароля вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="password_hash"):
            user_factory(password_hash="")

    def test_empty_first_name_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """Пустое имя вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="first_name"):
            user_factory(first_name="")

    def test_empty_last_name_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """Пустая фамилия вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="last_name"):
            user_factory(last_name="")

    def test_first_name_too_long_raises_error(self, user_factory: Callable[..., User]):
        """Имя длиннее максимума вызывает UserFirstNameTooLongError."""
        long_name = "A" * (USER_FIRST_NAME_MAX_LENGTH + 1)
        with pytest.raises(UserFirstNameTooLongError):
            user_factory(first_name=long_name)

    def test_first_name_at_max_length_accepted(self, user_factory: Callable[..., User]):
        """Имя ровно на максимуме длины проходит валидацию."""
        max_name = "A" * USER_FIRST_NAME_MAX_LENGTH
        user = user_factory(first_name=max_name)
        assert user.first_name == max_name

    def test_last_name_too_long_raises_error(self, user_factory: Callable[..., User]):
        """Фамилия длиннее максимума вызывает UserLastNameTooLongError."""
        long_name = "B" * (USER_LAST_NAME_MAX_LENGTH + 1)
        with pytest.raises(UserLastNameTooLongError):
            user_factory(last_name=long_name)

    def test_last_name_at_max_length_accepted(self, user_factory: Callable[..., User]):
        """Фамилия ровно на максимуме длины проходит валидацию."""
        max_name = "B" * USER_LAST_NAME_MAX_LENGTH
        user = user_factory(last_name=max_name)
        assert user.last_name == max_name

    def test_none_oid_raises_param_empty_error(self, user_factory: Callable[..., User]):
        """None в качестве domain_id вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="domain_id"):
            user_factory(oid=None)


class TestUserIdentity:
    """Тесты равенства и хеширования по identity (id)."""

    def test_users_with_same_id_are_equal(self, user_factory: Callable[..., User]):
        """Два User с одинаковым id считаются равными."""
        uid = uuid.uuid4()
        user1 = user_factory(oid=uid, login="alice")
        user2 = user_factory(oid=uid, login="bob")
        assert user1 == user2

    def test_users_with_different_id_are_not_equal(self, user_factory: Callable[..., User]):
        """Два User с разными id не равны."""
        user1 = user_factory(oid=uuid.uuid4())
        user2 = user_factory(oid=uuid.uuid4())
        assert user1 != user2

    def test_user_hash_depends_on_id(self, user_factory: Callable[..., User]):
        """Хэш User зависит только от id."""
        uid = uuid.uuid4()
        user1 = user_factory(oid=uid)
        user2 = user_factory(oid=uid)
        assert hash(user1) == hash(user2)

    def test_user_not_equal_to_non_entity(self, user_factory: Callable[..., User]):
        """User не равен объекту другого типа."""
        user = user_factory()
        assert user != "not_a_user"


class TestUserDomainEvents:
    """Тесты механизма доменных событий, унаследованного от BaseAggregate."""

    def test_domain_events_initially_empty(self, user_factory: Callable[..., User]):
        """У нового пользователя нет доменных событий."""
        user = user_factory()
        assert user.domain_events == []

    def test_raise_and_clear_domain_events(self, user_factory: Callable[..., User]):
        """Можно добавить и очистить доменные события."""
        user = user_factory()

        class FakeEvent:
            pass

        event = FakeEvent()
        user.raise_domain_event(event)
        assert len(user.domain_events) == 1
        assert user.domain_events[0] is event

        user.clear_domain_events()
        assert user.domain_events == []
