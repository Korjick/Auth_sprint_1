import datetime

from auth_api.internal.ports.output.time_provider import TimeProvider


class UtcTimeProvider(TimeProvider):
    def now_utc(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.timezone.utc)

    def from_timestamp(self, timestamp: int | float) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(
            timestamp,
            datetime.timezone.utc,
        )

