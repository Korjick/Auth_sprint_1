import datetime
import uuid

import jwt

from auth_api.internal.pkg.errors import UnauthorizedError
from auth_api.internal.ports.output.cache_provider import CacheProvider
from auth_api.internal.ports.output.time_provider import TimeProvider
from auth_api.internal.ports.output.token_provider import TokenProvider, \
    CreateTokenData, UserTokenData, DecodedTokenData


class PyJWTTokenProvider(TokenProvider):
    def __init__(self,
                 secret_key: str,
                 algorithm: str,
                 access_token_timedelta_minutes: int,
                 refresh_token_timedelta_days: int,
                 time_provider: TimeProvider,
                 cache_provider: CacheProvider):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_timedelta_minutes = access_token_timedelta_minutes
        self.refresh_token_timedelta_days = refresh_token_timedelta_days
        self._time = time_provider
        self._cache = cache_provider

    def create_token(self, token_data: CreateTokenData) -> str:
        delta = (
            datetime.timedelta(days=self.refresh_token_timedelta_days)
            if token_data.refresh
            else datetime.timedelta(
                minutes=self.access_token_timedelta_minutes)
        )
        payload = {
            'user': {
                'user_id': str(token_data.user.user_id),
                'roles': list(token_data.user.roles),
                'is_superuser': token_data.user.is_superuser
            },
            'refresh': token_data.refresh,
            'exp': self._time.now_utc() + delta,
            'jti': str(uuid.uuid4())
        }
        token = jwt.encode(
            payload=payload,
            key=self.secret_key,
            algorithm=self.algorithm,
        )
        return token

    def decode_token(self,
                     token: str) -> DecodedTokenData:
        try:
            token_data = jwt.decode(
                jwt=token,
                key=self.secret_key,
                algorithms=[self.algorithm],
            )
            user_data = token_data.pop('user')
            user_data = UserTokenData(user_id=uuid.UUID(user_data['user_id']),
                                      roles=user_data['roles'],
                                      is_superuser=user_data['is_superuser'])
            exp = self._time.from_timestamp(token_data.pop('exp'))
            jti = uuid.UUID(token_data.pop('jti'))
            refresh = token_data.pop('refresh')
            return DecodedTokenData(
                user=user_data,
                exp=exp,
                jti=jti,
                refresh=refresh,
            )
        except jwt.PyJWTError:
            raise UnauthorizedError()

    async def blacklist_token(self, jti: uuid.UUID) -> None:
        expire_sec = self.access_token_timedelta_minutes * 60
        await self._cache.cache_data(
            key=f"blacklist:{jti}",
            data="1",
            expire_sec=expire_sec,
        )

    async def is_token_blacklisted(self, jti: uuid.UUID) -> bool:
        result = await self._cache.get_from_cache(key=f"blacklist:{jti}")
        return result is not None

