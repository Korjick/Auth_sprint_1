from collections.abc import Callable

from auth_api.internal.core.application.services.token_pair import TokenPairService
from auth_api.internal.core.domain.models.user.user import User
from auth_api.internal.ports.output.token_provider import TokenProvider


def test_token_pair_decoded_data_vs_access_and_refresh_decoded_tokens(
    token_provider_factory: Callable[..., TokenProvider],
    user_factory: Callable[..., User],
):
    token_provider = token_provider_factory()
    service = TokenPairService(token_provider)
    user = user_factory()

    token_pair = service.create_for_user(user)

    decoded_access = token_provider.decode_token(token_pair.access_token.token)
    decoded_refresh = token_provider.decode_token(token_pair.refresh_token.token)

    assert decoded_access.jti == token_pair.access_token.jti
    assert decoded_access.exp == token_pair.access_token.exp
    assert decoded_refresh.jti == token_pair.refresh_token.jti
    assert decoded_refresh.exp == token_pair.refresh_token.exp

    assert decoded_access.user == decoded_refresh.user

