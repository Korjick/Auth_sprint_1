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
    DatabaseError,
    InfrastructureError,
    ValidationError,
)


class TestBaseEntity:
    """РўРµСЃС‚С‹ Р±Р°Р·РѕРІРѕРіРѕ РєР»Р°СЃСЃР° СЃСѓС‰РЅРѕСЃС‚Рё."""

    def test_entity_stores_id(self):
        """BaseEntity СЃРѕС…СЂР°РЅСЏРµС‚ РїРµСЂРµРґР°РЅРЅС‹Р№ id."""
        uid = uuid.uuid4()
        entity = BaseEntity(uid)
        assert entity.id == uid

    def test_entity_rejects_none_id(self):
        """None id РІС‹Р·С‹РІР°РµС‚ ParamEmptyError."""
        with pytest.raises(ParamEmptyError, match="domain_id"):
            BaseEntity(None)

    def test_entity_equality_by_id(self):
        """РЎСѓС‰РЅРѕСЃС‚Рё СЃ РѕРґРёРЅР°РєРѕРІС‹Рј id СЂР°РІРЅС‹."""
        uid = uuid.uuid4()
        e1 = BaseEntity(uid)
        e2 = BaseEntity(uid)
        assert e1 == e2

    def test_entity_inequality_different_id(self):
        """РЎСѓС‰РЅРѕСЃС‚Рё СЃ СЂР°Р·РЅС‹РјРё id РЅРµ СЂР°РІРЅС‹."""
        e1 = BaseEntity(uuid.uuid4())
        e2 = BaseEntity(uuid.uuid4())
        assert e1 != e2

    def test_entity_not_equal_to_other_type(self):
        """РЎСѓС‰РЅРѕСЃС‚СЊ РЅРµ СЂР°РІРЅР° РѕР±СЉРµРєС‚Сѓ РґСЂСѓРіРѕРіРѕ С‚РёРїР°."""
        e = BaseEntity(uuid.uuid4())
        assert e != 42

    def test_entity_hash_by_id(self):
        """РҐСЌС€ СЃСѓС‰РЅРѕСЃС‚Рё РѕСЃРЅРѕРІР°РЅ РЅР° id."""
        uid = uuid.uuid4()
        e1 = BaseEntity(uid)
        e2 = BaseEntity(uid)
        assert hash(e1) == hash(e2)


class TestBaseAggregate:
    """РўРµСЃС‚С‹ Р°РіСЂРµРіР°С‚Р° СЃ РґРѕРјРµРЅРЅС‹РјРё СЃРѕР±С‹С‚РёСЏРјРё."""

    def test_aggregate_has_empty_events(self):
        """РЈ РЅРѕРІРѕРіРѕ Р°РіСЂРµРіР°С‚Р° РЅРµС‚ РґРѕРјРµРЅРЅС‹С… СЃРѕР±С‹С‚РёР№."""
        agg = BaseAggregate(uuid.uuid4())
        assert agg.domain_events == []

    def test_raise_domain_event(self):
        """raise_domain_event РґРѕР±Р°РІР»СЏРµС‚ СЃРѕР±С‹С‚РёРµ."""
        agg = BaseAggregate(uuid.uuid4())
        event = {"type": "test"}
        agg.raise_domain_event(event)
        assert len(agg.domain_events) == 1

    def test_clear_domain_events(self):
        """clear_domain_events СѓРґР°Р»СЏРµС‚ РІСЃРµ СЃРѕР±С‹С‚РёСЏ."""
        agg = BaseAggregate(uuid.uuid4())
        agg.raise_domain_event({"type": "test"})
        agg.clear_domain_events()
        assert agg.domain_events == []

    def test_domain_events_returns_copy(self):
        """domain_events РІРѕР·РІСЂР°С‰Р°РµС‚ РєРѕРїРёСЋ СЃРїРёСЃРєР°."""
        agg = BaseAggregate(uuid.uuid4())
        event = {"type": "test"}
        agg.raise_domain_event(event)
        events = agg.domain_events
        events.clear()
        assert len(agg.domain_events) == 1


class TestErrors:
    """РўРµСЃС‚С‹ СЃРµСЂРёР°Р»РёР·Р°С†РёРё Рё СЃРѕРѕР±С‰РµРЅРёР№ РѕС€РёР±РѕРє."""

    def test_base_app_error_to_dict(self):
        """BaseAppError СЃРµСЂРёР°Р»РёР·СѓРµС‚СЃСЏ РІ dict СЃ code Рё message."""
        err = BaseAppError()
        d = err.to_dict()
        assert d["code"] == "INTERNAL_ERROR"
        assert "message" in d

    def test_param_empty_error_message(self):
        """ParamEmptyError СЃРѕРґРµСЂР¶РёС‚ РёРјСЏ РїР°СЂР°РјРµС‚СЂР° РІ СЃРѕРѕР±С‰РµРЅРёРё."""
        err = ParamEmptyError(param="login")
        assert "login must not be empty" in err.get_message()
        assert err.param == "login"

    def test_entity_not_found_error(self):
        """EntityNotFoundError СЃРѕРґРµСЂР¶РёС‚ РєР»СЋС‡ Рё РїР°СЂР°РјРµС‚СЂ."""
        err = EntityNotFoundError(param="id", key="123")
        assert "123" in err.get_message()
        assert err.code == "ENTITY_NOT_FOUND"

    def test_entity_already_exists_error(self):
        """EntityAlreadyExistsError СЃРѕРґРµСЂР¶РёС‚ РєР»СЋС‡ Рё РїР°СЂР°РјРµС‚СЂ."""
        err = EntityAlreadyExistsError(param="login", key="john")
        assert "john" in err.get_message()
        assert err.code == "ENTITY_ALREADY_EXISTS"

    def test_invalid_credentials_error(self):
        """InvalidCredentialsError РёРјРµРµС‚ РїСЂР°РІРёР»СЊРЅС‹Р№ РєРѕРґ."""
        err = InvalidCredentialsError()
        assert err.code == "INVALID_CREDENTIALS"
        assert "invalid login or password" in err.get_message()

    def test_unauthorized_error(self):
        """UnauthorizedError РёРјРµРµС‚ РїСЂР°РІРёР»СЊРЅС‹Р№ РєРѕРґ."""
        err = UnauthorizedError()
        assert err.code == "UNAUTHORIZED"

    def test_forbidden_error(self):
        """ForbiddenError РёРјРµРµС‚ РїСЂР°РІРёР»СЊРЅС‹Р№ РєРѕРґ."""
        err = ForbiddenError()
        assert err.code == "FORBIDDEN"

    def test_database_error(self):
        """DatabaseError РѕР±РѕСЂР°С‡РёРІР°РµС‚ РёСЃРєР»СЋС‡РµРЅРёРµ РёРЅС„СЂР°СЃС‚СЂСѓРєС‚СѓСЂС‹."""
        cause = RuntimeError("connection lost")
        err = DatabaseError(cause=cause)
        assert err.code == "DATABASE_ERROR"
        assert err.cause is cause

    def test_infrastructure_error(self):
        """InfrastructureError СЃРѕРґРµСЂР¶РёС‚ РёРјСЏ СЃРµСЂРІРёСЃР°."""
        err = InfrastructureError(service="redis")
        assert err.code == "INFRASTRUCTURE_ERROR"

    def test_validation_error_code(self):
        """ValidationError вЂ” Р±Р°Р·РѕРІС‹Р№ РєР»Р°СЃСЃ РґР»СЏ РѕС€РёР±РѕРє РІР°Р»РёРґР°С†РёРё."""
        err = ValidationError()
        assert err.code == "VALIDATION_ERROR"

    def test_error_details_in_to_dict(self):
        """Р”РµС‚Р°Р»Рё РѕС€РёР±РєРё РІРєР»СЋС‡Р°СЋС‚СЃСЏ РІ СЃРµСЂРёР°Р»РёР·Р°С†РёСЋ."""
        err = ParamEmptyError(param="login")
        d = err.to_dict()
        assert d["details"]["param"] == "login"

