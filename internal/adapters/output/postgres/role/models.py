import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import relationship, mapped_column, Mapped

from internal.adapters.output.postgres.models import Base
from internal.adapters.output.postgres.user.models import user_roles


class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {"schema": "service"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(10),
        unique=True,
    )
    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )

    def __repr__(self) -> str:
        return f'<Role {self.name}>'
