import datetime

from auth_api.internal.infrastructure.time_provider import UtcTimeProvider


class TestUtcTimeProvider:
    """РўРµСЃС‚С‹ РїСЂРѕРІР°Р№РґРµСЂР° РІСЂРµРјРµРЅРё UTC."""

    def setup_method(self):
        self.time_provider = UtcTimeProvider()

    def test_now_utc_returns_datetime(self):
        """now_utc РІРѕР·РІСЂР°С‰Р°РµС‚ РѕР±СЉРµРєС‚ datetime."""
        result = self.time_provider.now_utc()
        assert isinstance(result, datetime.datetime)

    def test_now_utc_is_naive(self):
        """now_utc РІРѕР·РІСЂР°С‰Р°РµС‚ naive datetime (Р±РµР· tzinfo)."""
        result = self.time_provider.now_utc()
        assert result.tzinfo is None

    def test_now_utc_is_close_to_current_time(self):
        """now_utc РІРѕР·РІСЂР°С‰Р°РµС‚ РІСЂРµРјСЏ, Р±Р»РёР·РєРѕРµ Рє С‚РµРєСѓС‰РµРјСѓ UTC."""
        before = (datetime.datetime.now(datetime.timezone.utc)
                  .replace(tzinfo=None))
        result = self.time_provider.now_utc()
        after = (datetime.datetime.now(datetime.timezone.utc)
                 .replace(tzinfo=None))
        assert before <= result <= after

    def test_from_timestamp_returns_datetime(self):
        """from_timestamp РІРѕР·РІСЂР°С‰Р°РµС‚ РѕР±СЉРµРєС‚ datetime."""
        ts = 1700000000
        result = self.time_provider.from_timestamp(ts)
        assert isinstance(result, datetime.datetime)

    def test_from_timestamp_is_naive(self):
        """from_timestamp РІРѕР·РІСЂР°С‰Р°РµС‚ naive datetime."""
        result = self.time_provider.from_timestamp(1700000000)
        assert result.tzinfo is None

    def test_from_timestamp_with_float(self):
        """from_timestamp РїСЂРёРЅРёРјР°РµС‚ float."""
        result = self.time_provider.from_timestamp(1700000000.5)
        assert isinstance(result, datetime.datetime)

