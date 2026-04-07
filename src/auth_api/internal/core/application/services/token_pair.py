import datetime
import uuid
from dataclasses import dataclass

from auth_api.internal.core.domain.models.user.user import User
from auth_api.internal.ports.output.token_provider import (
    CreateTokenData,
    TokenProvider,
    UserTokenData,
)


@dataclass(kw_only=True)
class TokenData:
    token: str
    exp: datetime.datetime
    jti: uuid.UUID


@dataclass(kw_only=True)
class TokenPair:
    access_token: TokenData
    refresh_token: TokenData


class TokenPairService:
    def __init__(self, token_provider: TokenProvider):
        self._tokens = token_provider

    def create_for_user(self, user: User) -> TokenPair:
        user_token = UserTokenData(
            user_id=user.id,
            roles=user.roles,
            is_superuser=user.is_superuser,
        )

        access_token = self._tokens.create_token(
            CreateTokenData(user=user_token, refresh=False)
        )
        refresh_token = self._tokens.create_token(
            CreateTokenData(user=user_token, refresh=True)
        )
        decoded_data_access = self._tokens.decode_token(access_token)
        decoded_data_refresh = self._tokens.decode_token(refresh_token)

        return TokenPair(
            access_token=TokenData(token=access_token,
                                   exp=decoded_data_access.exp,
                                   jti=decoded_data_access.jti),
            refresh_token=TokenData(token=refresh_token,
                                    exp=decoded_data_refresh.exp,
                                    jti=decoded_data_refresh.jti)
        )

