import uuid
import datetime
from collections.abc import Callable

import pytest

from internal.core.domain.models.session.session import Session
from internal.pkg.errors import ParamEmptyError


class TestSessionCreation:
    """Тесты создания сессии с корректными данными."""

    def test_create_valid_session(self, session_factory: Callable[..., Session]):
        """Сессия создаётся с корректными полями."""
        sid = uuid.uuid4()
        uid = uuid.uuid4()
        jti = uuid.uuid4()
        expire = datetime.datetime(2025, 6, 1)
        session = session_factory(
            oid=sid, user_id=uid, jti=jti,
            device_fingerprint="Chrome|ru|10.0.0.1",
            expire_at=expire,
        )

        assert session.id == sid
        assert session.user_id == uid
        assert session.jti == jti
        assert session.device_fingerprint == "Chrome|ru|10.0.0.1"
        assert session.expire_at == expire

    def test_session_fields_are_mutable(self, session_factory: Callable[..., Session]):
        """Поля jti и expire_at можно обновлять (для refresh)."""
        session = session_factory()
        new_jti = uuid.uuid4()
        new_expire = datetime.datetime(2025, 12, 31)

        session.jti = new_jti
        session.expire_at = new_expire

        assert session.jti == new_jti
        assert session.expire_at == new_expire


class TestSessionValidation:
    """Тесты валидации полей при создании Session."""

    def test_none_oid_raises_param_empty_error(self, session_factory: Callable[..., Session]):
        """None в качестве domain_id вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="domain_id"):
            session_factory(oid=None)

    def test_none_user_id_raises_param_empty_error(self, session_factory: Callable[..., Session]):
        """None user_id вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="user_id"):
            session_factory(user_id=None)

    def test_none_jti_raises_param_empty_error(self, session_factory: Callable[..., Session]):
        """None jti вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="jti"):
            session_factory(jti=None)

    def test_empty_device_fingerprint_raises_param_empty_error(self, session_factory: Callable[..., Session]):
        """Пустой device_fingerprint вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="device_fingerprint"):
            session_factory(device_fingerprint="")

    def test_none_expire_at_raises_param_empty_error(self, session_factory: Callable[..., Session]):
        """None expire_at вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="expire_at"):
            session_factory(expire_at=None)


class TestSessionIdentity:
    """Тесты равенства и хеширования по identity."""

    def test_sessions_with_same_id_are_equal(self, session_factory: Callable[..., Session]):
        """Две сессии с одинаковым id считаются равными."""
        sid = uuid.uuid4()
        s1 = session_factory(oid=sid)
        s2 = session_factory(oid=sid)
        assert s1 == s2

    def test_sessions_with_different_id_are_not_equal(self, session_factory: Callable[..., Session]):
        """Две сессии с разными id не равны."""
        s1 = session_factory(oid=uuid.uuid4())
        s2 = session_factory(oid=uuid.uuid4())
        assert s1 != s2

    def test_session_hash_depends_on_id(self, session_factory: Callable[..., Session]):
        """Хэш Session зависит только от id."""
        sid = uuid.uuid4()
        s1 = session_factory(oid=sid)
        s2 = session_factory(oid=sid)
        assert hash(s1) == hash(s2)

    def test_session_can_be_used_in_set(self, session_factory: Callable[..., Session]):
        """Сессии корректно работают в множествах."""
        sid = uuid.uuid4()
        s1 = session_factory(oid=sid)
        s2 = session_factory(oid=sid)
        s3 = session_factory(oid=uuid.uuid4())
        assert len({s1, s2, s3}) == 2
