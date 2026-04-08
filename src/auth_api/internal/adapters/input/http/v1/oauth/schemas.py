import datetime

from pydantic import BaseModel

from auth_api.internal.ports.input.oauth.oauth_handler import Flow


class LinkedSocialIdentityResponse(BaseModel):
    provider: str
    subject: str
    email: str | None
    email_verified: bool
    created_at: datetime.datetime


class GoogleOAuthCallbackResponse(BaseModel):
    flow: Flow
    access_token: str | None = None
    refresh_token: str | None = None
    identity: LinkedSocialIdentityResponse | None = None
