import datetime
import typing


class TimeProvider(typing.Protocol):
    def now_utc(self) -> datetime.datetime:
        ...

    def from_timestamp(self, timestamp: int | float) -> datetime.datetime:
        ...
