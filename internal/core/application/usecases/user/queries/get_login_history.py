from internal.core.domain.models.session.session import Session
from internal.ports.input.user.get_login_history_handler import (
    GetLoginHistory,
    GetLoginHistoryHandlerProtocol,
)
from internal.ports.output.uow import UnitOfWork


class GetLoginHistoryUseCase(GetLoginHistoryHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: GetLoginHistory) -> list[Session]:
        async with self._uow:
            sessions = await self._uow.sessions.get_sessions_by_user_id(
                user_id=query.user.user_id
            )
        return sorted(sessions, key=lambda item: item.expire_at, reverse=True)
