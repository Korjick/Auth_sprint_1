from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Path, Query, Request, Response, \
    status
from fastapi.responses import RedirectResponse

from auth_api.internal.adapters.input.http.dependencies import (
    access_token_required,
    get_device_fingerprint,
)
from auth_api.internal.adapters.input.http.v1.oauth.dependencies import (
    google_oauth_handler,
    list_social_identities_handler,
    unlink_social_identity_handler,
)
from auth_api.internal.adapters.input.http.v1.oauth.schemas import (
    GoogleOAuthCallbackResponse,
    LinkedSocialIdentityResponse,
)
from auth_api.internal.ports.input.oauth.oauth_handler import (
    CompleteOAuth,
    LinkedSocialIdentity,
    OAuthHandlerProtocol,
    StartOAuthLink,
)
from auth_api.internal.ports.input.oauth.list_social_identities_handler import (
    ListSocialIdentities,
    ListSocialIdentitiesHandlerProtocol,
)
from auth_api.internal.ports.input.oauth.unlink_social_identity_handler import (
    UnlinkSocialIdentity,
    UnlinkSocialIdentityHandlerProtocol,
)
from auth_api.internal.pkg.errors import UnauthorizedError
from auth_api.internal.ports.input.oauth.oauth_handler import Flow
from auth_api.internal.ports.output.token_provider import DecodedTokenData

router = APIRouter(prefix="/oauth", tags=["OAuth"])
OAUTH_STATE_COOKIE_NAME = "oauth_state_bind"
OAUTH_STATE_COOKIE_PATH = "/api/v1/oauth/google/callback"


@router.get(
    "/google/login",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def google_oauth_start(
        request: Request,
        handler: Annotated[
            OAuthHandlerProtocol,
            Depends(google_oauth_handler),
        ],
) -> RedirectResponse:
    started = await handler.start_login()
    response = RedirectResponse(
        url=started.authorization_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
    _set_oauth_state_cookie(
        response=response,
        request=request,
        state_binding=started.state_binding,
        max_age=request.app.state.settings.oauth_state_ttl_sec,
    )
    return response


@router.get(
    "/google/link",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def google_oauth_link_start(
        request: Request,
        user_details: Annotated[
            DecodedTokenData,
            Depends(access_token_required),
        ],
        handler: Annotated[
            OAuthHandlerProtocol,
            Depends(google_oauth_handler),
        ],
) -> RedirectResponse:
    started = await handler.start_link(
        StartOAuthLink(user_id=user_details.user.user_id)
    )
    response = RedirectResponse(
        url=started.authorization_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
    _set_oauth_state_cookie(
        response=response,
        request=request,
        state_binding=started.state_binding,
        max_age=request.app.state.settings.oauth_state_ttl_sec,
    )
    return response


@router.get(
    "/google/callback",
    response_model=GoogleOAuthCallbackResponse,
)
async def google_oauth_callback(
        response: Response,
        code: Annotated[str, Query(min_length=1)],
        state: Annotated[str, Query(min_length=1)],
        device_fingerprint: Annotated[str, Depends(get_device_fingerprint)],
        handler: Annotated[
            OAuthHandlerProtocol,
            Depends(google_oauth_handler),
        ],
        error: str | None = Query(default=None),
        error_description: str | None = Query(default=None),
        state_binding: Annotated[
            str | None,
            Cookie(alias=OAUTH_STATE_COOKIE_NAME),
        ] = None,
) -> GoogleOAuthCallbackResponse:
    if error is not None or error_description is not None:
        raise UnauthorizedError()

    result = await handler.complete(
        CompleteOAuth(
            code=code,
            state=state,
            state_binding=state_binding,
            device_fingerprint=device_fingerprint,
        )
    )
    response.delete_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        path=OAUTH_STATE_COOKIE_PATH,
    )
    return _to_callback_response(result.flow, result.access_session,
                                 result.refresh_session, result.identity)


@router.get(
    "/identities",
    response_model=list[LinkedSocialIdentityResponse],
)
async def list_linked_social_identities(
        user_details: Annotated[
            DecodedTokenData,
            Depends(access_token_required),
        ],
        handler: Annotated[
            ListSocialIdentitiesHandlerProtocol,
            Depends(list_social_identities_handler),
        ],
) -> list[LinkedSocialIdentityResponse]:
    identities = await handler.handle(
        ListSocialIdentities(user_id=user_details.user.user_id)
    )
    return [
        LinkedSocialIdentityResponse(
            provider=identity.provider,
            subject=identity.subject,
            email=identity.email,
            email_verified=identity.email_verified,
            created_at=identity.created_at,
        )
        for identity in identities
    ]


@router.delete(
    "/{provider}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlink_social_identity(
        provider: Annotated[str, Path(min_length=1)],
        user_details: Annotated[
            DecodedTokenData,
            Depends(access_token_required),
        ],
        handler: Annotated[
            UnlinkSocialIdentityHandlerProtocol,
            Depends(unlink_social_identity_handler),
        ],
) -> None:
    await handler.handle(
        UnlinkSocialIdentity(
            user_id=user_details.user.user_id,
            provider=provider,
        )
    )


def _to_callback_response(
        flow: Flow,
        access_token: str | None,
        refresh_token: str | None,
        identity: LinkedSocialIdentity | None,
) -> GoogleOAuthCallbackResponse:
    return GoogleOAuthCallbackResponse(
        flow=flow,
        access_token=access_token,
        refresh_token=refresh_token,
        identity=LinkedSocialIdentityResponse(
            provider=identity.provider,
            subject=identity.subject,
            email=identity.email,
            email_verified=identity.email_verified,
            created_at=identity.created_at,
        ) if identity is not None else None,
    )


def _set_oauth_state_cookie(
        response: Response,
        request: Request,
        state_binding: str,
        max_age: int,
) -> None:
    response.set_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        value=state_binding,
        max_age=max_age,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path=OAUTH_STATE_COOKIE_PATH,
    )
