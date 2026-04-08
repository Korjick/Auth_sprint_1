from fastapi import Depends, Request

from auth_api.internal.adapters.input.dependencies import (
    get_cache_provider,
    get_google_social_auth_provider,
    get_hash_provider,
    get_token_provider,
    get_uow,
)
from auth_api.internal.core.application.services.token_pair import TokenPairService
from auth_api.internal.core.application.usecases.oauth.commands.oauth import (
    OAuthUseCase,
)
from auth_api.internal.core.application.usecases.oauth.commands.unlink_social_identity import (
    UnlinkSocialIdentityUseCase,
)
from auth_api.internal.core.application.usecases.oauth.queries.list_social_identities import (
    ListSocialIdentitiesUseCase,
)
from auth_api.internal.ports.input.oauth.list_social_identities_handler import (
    ListSocialIdentitiesHandlerProtocol,
)
from auth_api.internal.ports.input.oauth.oauth_handler import (
    OAuthHandlerProtocol,
)
from auth_api.internal.ports.input.oauth.unlink_social_identity_handler import (
    UnlinkSocialIdentityHandlerProtocol,
)
from auth_api.internal.ports.output.cache_provider import CacheProvider
from auth_api.internal.ports.output.hash_provider import HashProvider
from auth_api.internal.ports.output.social_auth_provider import SocialAuthProvider
from auth_api.internal.ports.output.token_provider import TokenProvider
from auth_api.internal.ports.output.uow import UnitOfWork


def token_pair_service(
        token_provider: TokenProvider = Depends(get_token_provider),
) -> TokenPairService:
    return TokenPairService(token_provider)


def google_oauth_handler(
        request: Request,
        cache_provider: CacheProvider = Depends(get_cache_provider),
        social_auth_provider: SocialAuthProvider = Depends(
            get_google_social_auth_provider
        ),
        uow: UnitOfWork = Depends(get_uow),
        hash_provider: HashProvider = Depends(get_hash_provider),
        token_pairs: TokenPairService = Depends(token_pair_service),
) -> OAuthHandlerProtocol:
    state_ttl_sec = request.app.state.settings.oauth_state_ttl_sec
    return OAuthUseCase(
        cache_provider=cache_provider,
        social_auth_provider=social_auth_provider,
        uow=uow,
        hash_provider=hash_provider,
        token_pair_service=token_pairs,
        state_ttl_sec=state_ttl_sec,
    )


def list_social_identities_handler(
        uow: UnitOfWork = Depends(get_uow),
) -> ListSocialIdentitiesHandlerProtocol:
    return ListSocialIdentitiesUseCase(uow=uow)


def unlink_social_identity_handler(
        uow: UnitOfWork = Depends(get_uow),
) -> UnlinkSocialIdentityHandlerProtocol:
    return UnlinkSocialIdentityUseCase(uow=uow)
