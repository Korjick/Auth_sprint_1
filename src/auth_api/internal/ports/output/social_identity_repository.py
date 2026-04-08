import uuid
from dataclasses import dataclass
from typing import Protocol

from auth_api.internal.core.domain.models.social_identity.social_identity import (
    SocialIdentity,
)


@dataclass(kw_only=True)
class SocialIdentityCreate:
    user_id: uuid.UUID
    provider: str
    subject: str
    email: str | None = None
    email_verified: bool = False


class SocialIdentityRepository(Protocol):
    async def create_identity(
            self,
            identity_to_create: SocialIdentityCreate,
    ) -> SocialIdentity:
        ...

    async def get_by_provider_subject(
            self,
            provider: str,
            subject: str,
    ) -> SocialIdentity:
        ...

    async def get_by_user_provider(
            self,
            user_id: uuid.UUID,
            provider: str,
    ) -> SocialIdentity:
        ...

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[SocialIdentity]:
        ...

    async def delete_by_user_provider(
            self,
            user_id: uuid.UUID,
            provider: str,
    ) -> None:
        ...
