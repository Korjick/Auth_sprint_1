import datetime
import enum
import uuid
from dataclasses import dataclass
from typing import Protocol


class Flow(enum.StrEnum):
    LOGIN = "login"
    LINK = "link"


@dataclass(kw_only=True)
class StartedOAuth:
    authorization_url: str
    state_binding: str


@dataclass(kw_only=True)
class StartOAuthLink:
    user_id: uuid.UUID


@dataclass(kw_only=True)
class CompleteOAuth:
    code: str
    state: str
    state_binding: str | None
    device_fingerprint: str


@dataclass(kw_only=True)
class LinkedSocialIdentity:
    provider: str
    subject: str
    email: str | None
    email_verified: bool
    created_at: datetime.datetime


@dataclass(kw_only=True)
class OAuthCompleted:
    flow: Flow
    access_session: str | None = None
    refresh_session: str | None = None
    identity: LinkedSocialIdentity | None = None


class OAuthHandlerProtocol(Protocol):
    async def start_login(self) -> StartedOAuth:
        ...

    async def start_link(self, command: StartOAuthLink) -> StartedOAuth:
        ...

    async def complete(self, command: CompleteOAuth) -> OAuthCompleted:
        ...
