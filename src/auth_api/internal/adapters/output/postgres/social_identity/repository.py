import uuid

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_api.internal.adapters.output.postgres.social_identity.models import (
    SocialIdentity as SocialIdentityModel,
)
from auth_api.internal.core.domain.models.social_identity.social_identity import (
    SocialIdentity as DomainSocialIdentity,
)
from auth_api.internal.pkg.errors import EntityNotFoundError
from auth_api.internal.ports.output.social_identity_repository import (
    SocialIdentityCreate,
    SocialIdentityRepository,
)


class PostgresSocialIdentityRepository(SocialIdentityRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    @staticmethod
    def _to_domain(row: SocialIdentityModel) -> DomainSocialIdentity:
        return DomainSocialIdentity(
            oid=row.id,
            user_id=row.user_id,
            provider=row.provider,
            subject=row.subject,
            email=row.email,
            email_verified=row.email_verified,
            created_at=row.created_at,
        )

    async def create_identity(
            self,
            identity_to_create: SocialIdentityCreate,
    ) -> DomainSocialIdentity:
        row = SocialIdentityModel(
            user_id=identity_to_create.user_id,
            provider=identity_to_create.provider.strip().lower(),
            subject=identity_to_create.subject.strip(),
            email=identity_to_create.email.strip()
            if identity_to_create.email is not None
            else None,
            email_verified=identity_to_create.email_verified,
        )
        self._db_session.add(row)
        await self._db_session.flush()
        return self._to_domain(row)

    async def get_by_provider_subject(
            self,
            provider: str,
            subject: str,
    ) -> DomainSocialIdentity:
        provider_key = provider.strip().lower()
        subject_key = subject.strip()
        result = await self._db_session.execute(
            select(SocialIdentityModel).where(
                and_(
                    SocialIdentityModel.provider == provider_key,
                    SocialIdentityModel.subject == subject_key,
                )
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(
                param="provider_subject",
                key=f"{provider_key}:{subject_key}",
            )
        return self._to_domain(row)

    async def get_by_user_provider(
            self,
            user_id: uuid.UUID,
            provider: str,
    ) -> DomainSocialIdentity:
        provider_key = provider.strip().lower()
        result = await self._db_session.execute(
            select(SocialIdentityModel).where(
                and_(
                    SocialIdentityModel.user_id == user_id,
                    SocialIdentityModel.provider == provider_key,
                )
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(
                param="user_provider",
                key=f"{user_id}:{provider_key}",
            )
        return self._to_domain(row)

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[DomainSocialIdentity]:
        result = await self._db_session.execute(
            select(SocialIdentityModel).where(SocialIdentityModel.user_id == user_id)
        )
        rows = result.scalars().all()
        return [self._to_domain(row) for row in rows]

    async def delete_by_user_provider(
            self,
            user_id: uuid.UUID,
            provider: str,
    ) -> None:
        provider_key = provider.strip().lower()
        await self._db_session.execute(
            delete(SocialIdentityModel).where(
                and_(
                    SocialIdentityModel.user_id == user_id,
                    SocialIdentityModel.provider == provider_key,
                )
            )
        )
        await self._db_session.flush()

