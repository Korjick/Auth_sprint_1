from dataclasses import dataclass
from typing import Protocol

from internal.core.domain.models.session.session import Session
from internal.ports.output.token_provider import UserTokenData


@dataclass(kw_only=True)
class GetLoginHistory:
    user: UserTokenData


class GetLoginHistoryHandlerProtocol(Protocol):
    async def handle(self, query: GetLoginHistory) -> list[Session]:
        ...
