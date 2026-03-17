import typing
import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class UserTokenData:
    user_id: uuid.UUID
    roles: typing.List[str]
    is_superuser: bool


@dataclass(kw_only=True)
class CreateTokenData:
    user: UserTokenData
    refresh: bool


@dataclass(kw_only=True)
class DecodedTokenData(CreateTokenData):
    exp: datetime
    jti: uuid.UUID


class TokenProvider(typing.Protocol):
    def create_token(
            self,
            token_data: CreateTokenData
    ) -> str:
        ...

    def decode_token(self,
                     token: str) -> DecodedTokenData:
        ...

    async def blacklist_token(self, jti: uuid.UUID) -> None:
        ...

    async def is_token_blacklisted(self, jti: uuid.UUID) -> bool:
        ...
