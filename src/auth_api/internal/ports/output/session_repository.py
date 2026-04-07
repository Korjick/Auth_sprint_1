import datetime
import typing
import uuid
from dataclasses import dataclass

from auth_api.internal.core.domain.models.session.session import Session


@dataclass(kw_only=True)
class SessionCreate:
    user_id: uuid.UUID
    jti: uuid.UUID
    device_fingerprint: str
    expires_at: datetime.datetime


class SessionRepository(typing.Protocol):
    async def create_session(self, session_create: SessionCreate) -> Session:
        ...

    async def update_session(self, session: Session) -> Session:
        ...

    async def delete_session(self, session_id: uuid.UUID) -> None:
        ...

    async def get_session_by_jti(self, jti: uuid.UUID) -> Session:
        ...

    async def get_sessions_by_user_id(
            self, user_id: uuid.UUID,
    ) -> typing.List[Session]:
        ...

    async def delete_by_user_id_and_fingerprint(
            self,
            user_id: uuid.UUID,
            device_fingerprint: str,
    ) -> None:
        ...

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        ...

