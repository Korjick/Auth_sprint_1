import datetime
import uuid
from dataclasses import dataclass
from typing import Protocol


@dataclass(kw_only=True)
class ListSocialIdentities:
    user_id: uuid.UUID


@dataclass(kw_only=True)
class SocialIdentityView:
    provider: str
    subject: str
    email: str | None
    email_verified: bool
    created_at: datetime.datetime


class ListSocialIdentitiesHandlerProtocol(Protocol):
    async def handle(
            self,
            query: ListSocialIdentities,
    ) -> list[SocialIdentityView]:
        ...
