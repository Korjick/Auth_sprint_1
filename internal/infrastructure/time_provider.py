import datetime

from internal.ports.output.time_provider import TimeProvider


class UtcTimeProvider(TimeProvider):
    def now_utc(self) -> datetime.datetime:
        return (datetime.datetime.now(datetime.timezone.utc)
                .replace(tzinfo=None))

    def from_timestamp(self, timestamp: int | float) -> datetime.datetime:
        return (datetime.datetime.fromtimestamp(timestamp)
                .replace(tzinfo=None))
