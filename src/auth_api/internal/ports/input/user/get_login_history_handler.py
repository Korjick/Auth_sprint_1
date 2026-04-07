from dataclasses import dataclass
from typing import Protocol

from auth_api.internal.core.domain.models.session.session import Session
from auth_api.internal.ports.output.token_provider import UserTokenData


@dataclass(kw_only=True)
class GetLoginHistory:
    user: UserTokenData


class GetLoginHistoryHandlerProtocol(Protocol):
    async def handle(self, query: GetLoginHistory) -> list[Session]:
        ...

