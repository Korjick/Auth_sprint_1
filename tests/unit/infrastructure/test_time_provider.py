import datetime

from auth_api.internal.infrastructure.time_provider import UtcTimeProvider


class TestUtcTimeProvider:
    """Тесты провайдера времени UTC."""

    def setup_method(self):
        self.time_provider = UtcTimeProvider()

    def test_now_utc_returns_datetime(self):
        """now_utc возвращает объект datetime."""
        result = self.time_provider.now_utc()
        assert isinstance(result, datetime.datetime)

    def test_now_utc_is_aware_utc(self):
        """now_utc возвращает aware datetime в UTC."""
        result = self.time_provider.now_utc()
        assert result.tzinfo == datetime.timezone.utc

    def test_now_utc_is_close_to_current_time(self):
        """now_utc возвращает время, близкое к текущему UTC."""
        before = datetime.datetime.now(datetime.timezone.utc)
        result = self.time_provider.now_utc()
        after = datetime.datetime.now(datetime.timezone.utc)
        assert before <= result <= after

    def test_from_timestamp_returns_datetime(self):
        """from_timestamp возвращает объект datetime."""
        ts = 1700000000
        result = self.time_provider.from_timestamp(ts)
        assert isinstance(result, datetime.datetime)

    def test_from_timestamp_is_aware_utc(self):
        """from_timestamp возвращает aware datetime в UTC."""
        result = self.time_provider.from_timestamp(1700000000)
        assert result.tzinfo == datetime.timezone.utc

    def test_from_timestamp_with_float(self):
        """from_timestamp принимает float timestamp."""
        result = self.time_provider.from_timestamp(1700000000.5)
        assert isinstance(result, datetime.datetime)
