from dataclasses import dataclass
from typing import Protocol


@dataclass(kw_only=True)
class SocialAuthProfile:
    provider: str
    subject: str
    email: str | None = None
    email_verified: bool = False
    first_name: str | None = None
    last_name: str | None = None


class SocialAuthProvider(Protocol):
    @property
    def name(self) -> str:
        ...

    def build_authorization_url(
            self,
            *,
            state: str,
    ) -> str:
        ...

    async def exchange_code(
            self,
            *,
            code: str,
    ) -> SocialAuthProfile:
        ...
