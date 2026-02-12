from typing import Annotated

from fastapi import Request, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from internal.adapters.input.dependencies import get_token_provider
from internal.core.domain.models.role.role import ADMIN_ROLE_NAME
from internal.pkg.errors import ForbiddenError, UnauthorizedError
from internal.ports.output.token_provider import TokenProvider, \
    DecodedTokenData

token_header = HTTPBearer(auto_error=False)


async def get_device_fingerprint(request: Request) -> str:
    user_agent = request.headers.get("user-agent", "")
    accept_lang = request.headers.get("accept-language", "")
    ip_address = request.client.host if request.client else "unknown"
    return f"{user_agent}|{accept_lang}|{ip_address}"


async def _auth_required(
        creds: Annotated[
            HTTPAuthorizationCredentials, Security(token_header)
        ],
        token_provider: Annotated[
            TokenProvider, Depends(get_token_provider)
        ],
) -> DecodedTokenData:
    if not creds:
        raise UnauthorizedError()

    payload = token_provider.decode_token(creds.credentials)
    if not payload:
        raise UnauthorizedError()

    return payload


async def access_token_required(
        token_data: Annotated[
            DecodedTokenData, Depends(_auth_required)
        ],
        token_provider: Annotated[
            TokenProvider, Depends(get_token_provider)
        ],
) -> DecodedTokenData:
    if token_data.refresh:
        raise ForbiddenError()
    if await token_provider.is_token_blacklisted(token_data.jti):
        raise UnauthorizedError()
    return token_data


async def refresh_token_required(
        token_data: Annotated[
            DecodedTokenData, Depends(_auth_required)
        ],
) -> DecodedTokenData:
    if not token_data.refresh:
        raise ForbiddenError()
    return token_data


def role_required_or_superuser(allowed_roles: list[str]):
    async def _checker(
            token_data: Annotated[
                DecodedTokenData, Depends(access_token_required)
            ],
    ) -> DecodedTokenData:
        if token_data.user.is_superuser:
            return token_data

        user_roles = set(token_data.user.roles)

        if not user_roles.intersection(allowed_roles):
            raise ForbiddenError()

        return token_data

    return _checker


admin_only = role_required_or_superuser([ADMIN_ROLE_NAME])
