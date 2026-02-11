import uuid
from typing import List

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from internal.adapters.output.postgres.session.models import \
    Session as SessionModel
from internal.core.domain.models.session.session import Session \
    as DomainSession
from internal.pkg.errors import EntityNotFoundError
from internal.ports.output.session_repository import SessionRepository, \
    SessionCreate


class PostgresSessionRepository(SessionRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def create_session(self,
                             session_create: SessionCreate) -> DomainSession:
        session_model = SessionModel(
            user_id=session_create.user_id,
            jti=session_create.jti,
            device_fingerprint=session_create.device_fingerprint,
            expires_at=session_create.expires_at,
        )
        self._db_session.add(session_model)
        await self._db_session.flush()
        return DomainSession(
            oid=session_model.id,
            jti=session_model.jti,
            device_fingerprint=session_model.device_fingerprint,
            expire_at=session_model.expires_at,
            user_id=session_model.user_id
        )

    async def update_session(self, session: DomainSession) -> DomainSession:
        result = await self._db_session.execute(
            select(SessionModel).where(SessionModel.id == session.id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(key=str(session.id), param='id')
        row.user_id = session.user_id
        row.jti = session.jti
        row.device_fingerprint = session.device_fingerprint
        row.expires_at = session.expire_at
        await self._db_session.flush()
        return DomainSession(
            oid=row.id,
            user_id=row.user_id,
            jti=row.jti,
            device_fingerprint=row.device_fingerprint,
            expire_at=row.expires_at
        )

    async def delete_session(self, session_id: uuid.UUID) -> None:
        await self._db_session.execute(
            delete(SessionModel).where(SessionModel.jti == session_id)
        )
        await self._db_session.flush()

    async def get_session_by_jti(self, jti: uuid.UUID) -> DomainSession:
        result = await self._db_session.execute(
            select(SessionModel).where(SessionModel.jti == jti)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(key=str(jti), param='jti')
        return DomainSession(
            oid=row.id,
            user_id=row.user_id,
            jti=row.jti,
            device_fingerprint=row.device_fingerprint,
            expire_at=row.expires_at
        )

    async def get_sessions_by_user_id(
            self, user_id: uuid.UUID,
    ) -> List[DomainSession]:
        result = await self._db_session.execute(
            select(SessionModel).where(SessionModel.user_id == user_id)
        )
        rows = result.scalars().all()
        return [
            DomainSession(
                oid=row.id,
                user_id=row.user_id,
                jti=row.jti,
                device_fingerprint=row.device_fingerprint,
                expire_at=row.expires_at
            ) for row in rows
        ]

    async def delete_by_user_id_and_fingerprint(
            self,
            user_id: uuid.UUID,
            device_fingerprint: str,
    ) -> None:
        await self._db_session.execute(
            delete(SessionModel).where(
                and_(
                    SessionModel.user_id == user_id,
                    SessionModel.device_fingerprint
                    == device_fingerprint,
                )
            )
        )
        await self._db_session.flush()

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        await self._db_session.execute(
            delete(SessionModel).where(SessionModel.user_id == user_id)
        )
        await self._db_session.flush()
