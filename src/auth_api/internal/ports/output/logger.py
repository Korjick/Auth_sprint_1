from typing import Any, Protocol, Self


class Logger(Protocol):
    def branch(self, **fields: Any) -> Self:
        ...

    def bind_context(self, **fields: Any) -> None:
        ...

    def clear_context(self) -> None:
        ...

    def debug(self, event: str, **fields: Any) -> None:
        ...

    def info(self, event: str, **fields: Any) -> None:
        ...

    def warning(self, event: str, **fields: Any) -> None:
        ...

    def error(self, event: str, **fields: Any) -> None:
        ...

    def exception(self, event: str, **fields: Any) -> None:
        ...
