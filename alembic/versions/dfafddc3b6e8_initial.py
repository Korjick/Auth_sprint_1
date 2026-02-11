"""Initial

Revision ID: dfafddc3b6e8
Revises: 
Create Date: 2026-02-09 03:42:59.390464

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from internal.core.domain.models.role.role import ADMIN_ROLE_NAME

revision: str = 'dfafddc3b6e8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS service;")
    roles_table = op.create_table('roles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    schema='service'
    )
    op.bulk_insert(
        roles_table,
        [
            {"id": uuid.uuid4(), "name": ADMIN_ROLE_NAME},
        ],
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('login', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('login'),
    schema='service'
    )
    op.create_table('sessions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('jti', sa.UUID(), nullable=False),
    sa.Column('device_fingerprint', sa.String(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['service.users.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='service'
    )
    op.create_index(op.f('ix_service_sessions_jti'), 'sessions', ['jti'], unique=False, schema='service')
    op.create_table('user_roles',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['service.roles.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['service.users.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'role_id'),
    schema='service'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_roles', schema='service')
    op.drop_index(op.f('ix_service_sessions_jti'), table_name='sessions', schema='service')
    op.drop_table('sessions', schema='service')
    op.drop_table('users', schema='service')
    op.drop_table('roles', schema='service')
    op.execute("DROP SCHEMA IF EXISTS service;")
