import uuid

import pytest

from auth_api.internal.pkg.domain import BaseEntity, BaseAggregate
from auth_api.internal.pkg.errors import (
    BaseAppError,
    ParamEmptyError,
    EntityNotFoundError,
    EntityAlreadyExistsError,
    InvalidCredentialsError,
    UnauthorizedError,
    ForbiddenError,
    FeatureDisabledError,
    RateLimitExceededError,
    DatabaseError,
    InfrastructureError,
    ValidationError,
)


class TestBaseEntity:
    """Тесты базового класса сущности."""

    def test_entity_stores_id(self):
        """BaseEntity сохраняет переданный id."""
        uid = uuid.uuid4()
        entity = BaseEntity(uid)
        assert entity.id == uid

    def test_entity_rejects_none_id(self):
        """None id вызывает ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="domain_id"):
            BaseEntity(None)

    def test_entity_equality_by_id(self):
        """Сущности с одинаковым id равны."""
        uid = uuid.uuid4()
        e1 = BaseEntity(uid)
        e2 = BaseEntity(uid)
        assert e1 == e2

    def test_entity_inequality_different_id(self):
        """Сущности с разными id не равны."""
        e1 = BaseEntity(uuid.uuid4())
        e2 = BaseEntity(uuid.uuid4())
        assert e1 != e2

    def test_entity_not_equal_to_other_type(self):
        """Сущность не равна объекту другого типа."""
        e = BaseEntity(uuid.uuid4())
        assert e != 42

    def test_entity_hash_by_id(self):
        """Хэш сущности основан на id."""
        uid = uuid.uuid4()
        e1 = BaseEntity(uid)
        e2 = BaseEntity(uid)
        assert hash(e1) == hash(e2)


class TestBaseAggregate:
    """Тесты агрегата с доменными событиями."""

    def test_aggregate_has_empty_events(self):
        """У нового агрегата нет доменных событий."""
        agg = BaseAggregate(uuid.uuid4())
        assert agg.domain_events == []

    def test_raise_domain_event(self):
        """raise_domain_event добавляет событие."""
        agg = BaseAggregate(uuid.uuid4())
        event = {"type": "test"}
        agg.raise_domain_event(event)
        assert len(agg.domain_events) == 1

    def test_clear_domain_events(self):
        """clear_domain_events удаляет все события."""
        agg = BaseAggregate(uuid.uuid4())
        agg.raise_domain_event({"type": "test"})
        agg.clear_domain_events()
        assert agg.domain_events == []

    def test_domain_events_returns_copy(self):
        """domain_events возвращает копию списка."""
        agg = BaseAggregate(uuid.uuid4())
        event = {"type": "test"}
        agg.raise_domain_event(event)
        events = agg.domain_events
        events.clear()
        assert len(agg.domain_events) == 1


class TestErrors:
    """Тесты сериализации и сообщений ошибок."""

    def test_base_app_error_to_dict(self):
        """BaseAppError сериализуется в dict с code и message."""
        err = BaseAppError()
        d = err.to_dict()
        assert d["code"] == "INTERNAL_ERROR"
        assert "message" in d

    def test_param_empty_error_message(self):
        """ParamEmptyError содержит имя параметра в сообщении."""
        err = ParamEmptyError(param="login")
        assert "login must not be empty" in err.get_message()
        assert err.param == "login"

    def test_entity_not_found_error(self):
        """EntityNotFoundError содержит ключ и параметр."""
        err = EntityNotFoundError(param="id", key="123")
        assert "123" in err.get_message()
        assert err.code == "ENTITY_NOT_FOUND"

    def test_entity_already_exists_error(self):
        """EntityAlreadyExistsError содержит ключ и параметр."""
        err = EntityAlreadyExistsError(param="login", key="john")
        assert "john" in err.get_message()
        assert err.code == "ENTITY_ALREADY_EXISTS"

    def test_invalid_credentials_error(self):
        """InvalidCredentialsError имеет правильный код."""
        err = InvalidCredentialsError()
        assert err.code == "INVALID_CREDENTIALS"
        assert "invalid login or password" in err.get_message()

    def test_unauthorized_error(self):
        """UnauthorizedError имеет правильный код."""
        err = UnauthorizedError()
        assert err.code == "UNAUTHORIZED"

    def test_forbidden_error(self):
        """ForbiddenError имеет правильный код."""
        err = ForbiddenError()
        assert err.code == "FORBIDDEN"

    def test_rate_limit_error(self):
        """RateLimitExceededError имеет правильный код."""
        err = RateLimitExceededError(
            limit=5,
            retry_after=10,
            reset_at=100,
            bucket="login_ip",
        )
        assert err.code == "RATE_LIMIT_EXCEEDED"
        assert err.details["retry_after"] == 10

    def test_database_error(self):
        """DatabaseError оборачивает исключение инфраструктуры."""
        cause = RuntimeError("connection lost")
        err = DatabaseError(cause=cause)
        assert err.code == "DATABASE_ERROR"
        assert err.cause is cause

    def test_infrastructure_error(self):
        """InfrastructureError содержит имя сервиса."""
        err = InfrastructureError(service="redis")
        assert err.code == "INFRASTRUCTURE_ERROR"
        assert err.cause is None

    def test_feature_disabled_error(self):
        err = FeatureDisabledError(feature="google_oauth")
        assert err.code == "FEATURE_DISABLED"
        assert "google_oauth is disabled" in err.get_message()
        assert err.details["feature"] == "google_oauth"

    def test_validation_error_code(self):
        """ValidationError — базовый класс для ошибок валидации."""
        err = ValidationError()
        assert err.code == "VALIDATION_ERROR"

    def test_error_details_in_to_dict(self):
        """Детали ошибки включаются в сериализацию."""
        err = ParamEmptyError(param="login")
        d = err.to_dict()
        assert d["details"]["param"] == "login"

