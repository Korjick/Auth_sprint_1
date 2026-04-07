import datetime
import uuid

from sqlalchemy import UUID, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from auth_api.internal.adapters.output.postgres.models import Base, PrimaryUUIDKey


class Session(Base):
    __tablename__ = 'sessions'
    __table_args__ = {"schema": "service"}

    id: Mapped[PrimaryUUIDKey]
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('service.users.id',
                   ondelete='CASCADE',
                   onupdate='CASCADE')
    )
    jti: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                           index=True)
    device_fingerprint: Mapped[str]
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime,
                                                          nullable=False)

