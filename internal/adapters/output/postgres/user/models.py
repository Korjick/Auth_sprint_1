import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, UUID, \
    Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from internal.adapters.output.postgres.models import Base, PrimaryUUIDKey

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id",
           UUID(as_uuid=True),
           ForeignKey("service.users.id",
                      ondelete='CASCADE',
                      onupdate='CASCADE'),
           primary_key=True),
    Column("role_id",
           UUID(as_uuid=True),
           ForeignKey("service.roles.id",
                      ondelete='CASCADE',
                      onupdate='CASCADE'),
           primary_key=True),
    schema="service",
)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "service"}

    id: Mapped[PrimaryUUIDKey]
    login: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean,
                                               nullable=False,
                                               default=False)
    is_active: Mapped[bool] = mapped_column(Boolean,
                                            nullable=False,
                                            default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(
            tzinfo=None)
    )

    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )

    def __init__(
            self,
            *,
            login: str,
            first_name: str,
            last_name: str,
            password_hash: str,
    ):
        super().__init__()
        self.login = login
        self.first_name = first_name
        self.last_name = last_name
        self.password_hash = password_hash

    def __repr__(self) -> str:
        return f'<User {self.login}>'
