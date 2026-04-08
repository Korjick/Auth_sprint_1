"""Partition sessions by expires_at.

Revision ID: d4a1e8b2c9f0
Revises: b8f4c7d3e1a2
Create Date: 2026-04-08 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d4a1e8b2c9f0"
down_revision: Union[str, Sequence[str], None] = "b8f4c7d3e1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS partman;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_partman SCHEMA partman;")
    op.execute("ALTER TABLE service.sessions RENAME TO sessions_old;")
    op.execute(
        """
        CREATE TABLE service.sessions (
            id UUID NOT NULL,
            user_id UUID NOT NULL,
            jti UUID NOT NULL,
            device_fingerprint VARCHAR NOT NULL,
            expires_at TIMESTAMPTZ NOT NULL,
            CONSTRAINT sessions_pk PRIMARY KEY (id, expires_at),
            CONSTRAINT sessions_user_id_fkey
                FOREIGN KEY (user_id)
                REFERENCES service.users(id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        ) PARTITION BY RANGE (expires_at);
        """
    )
    op.execute(
        """
        DO $$
        DECLARE
            min_month TIMESTAMPTZ;
        BEGIN
            SELECT date_trunc('month', MIN(expires_at))
            INTO min_month
            FROM service.sessions_old;

            IF min_month IS NULL THEN
                min_month := date_trunc('month', now());
            END IF;

            IF EXISTS (
                SELECT 1
                FROM pg_proc p
                JOIN pg_namespace n
                    ON n.oid = p.pronamespace
                WHERE n.nspname = 'partman'
                  AND p.proname = 'create_parent'
            ) THEN
                PERFORM partman.create_parent(
                    p_parent_table := 'service.sessions',
                    p_control := 'expires_at',
                    p_interval := '1 month',
                    p_type := 'range',
                    p_premake := 3,
                    p_start_partition := min_month::text,
                    p_default_table := true
                );
            ELSIF EXISTS (
                SELECT 1
                FROM pg_proc p
                JOIN pg_namespace n
                    ON n.oid = p.pronamespace
                WHERE n.nspname = 'partman'
                  AND p.proname = 'create_partition'
            ) THEN
                PERFORM partman.create_partition(
                    p_parent_table := 'service.sessions',
                    p_control := 'expires_at',
                    p_interval := '1 month',
                    p_type := 'range',
                    p_premake := 3,
                    p_start_partition := min_month::text,
                    p_default_table := true
                );
            ELSE
                RAISE EXCEPTION
                    'pg_partman function create_parent/create_partition was not found';
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        INSERT INTO service.sessions (
            id,
            user_id,
            jti,
            device_fingerprint,
            expires_at
        )
        SELECT
            id,
            user_id,
            jti,
            device_fingerprint,
            expires_at
        FROM service.sessions_old;
        """
    )
    op.execute("DROP TABLE service.sessions_old;")
    op.execute(
        """
        CREATE INDEX ix_service_sessions_jti_v2
        ON service.sessions (jti);
        """
    )
    op.execute(
        """
        CREATE INDEX ix_service_sessions_user_id_v2
        ON service.sessions (user_id);
        """
    )
    op.execute(
        """
        CREATE INDEX ix_service_sessions_user_id_device_fingerprint_v2
        ON service.sessions (user_id, device_fingerprint);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'partman'
                  AND table_name = 'part_config'
            ) THEN
                DELETE FROM partman.part_config
                WHERE parent_table = 'service.sessions';
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        CREATE TABLE service.sessions_plain (
            id UUID NOT NULL,
            user_id UUID NOT NULL,
            jti UUID NOT NULL,
            device_fingerprint VARCHAR NOT NULL,
            expires_at TIMESTAMPTZ NOT NULL,
            CONSTRAINT sessions_plain_pk PRIMARY KEY (id),
            CONSTRAINT sessions_plain_user_id_fkey
                FOREIGN KEY (user_id)
                REFERENCES service.users(id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        );
        """
    )
    op.execute(
        """
        INSERT INTO service.sessions_plain (
            id,
            user_id,
            jti,
            device_fingerprint,
            expires_at
        )
        SELECT DISTINCT ON (id)
            id,
            user_id,
            jti,
            device_fingerprint,
            expires_at
        FROM service.sessions
        ORDER BY id, expires_at DESC;
        """
    )
    op.execute("DROP TABLE service.sessions CASCADE;")
    op.execute("ALTER TABLE service.sessions_plain RENAME TO sessions;")
    op.execute(
        """
        CREATE INDEX ix_service_sessions_jti
        ON service.sessions (jti);
        """
    )
