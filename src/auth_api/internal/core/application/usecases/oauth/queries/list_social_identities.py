from auth_api.internal.ports.input.oauth.list_social_identities_handler import (
    ListSocialIdentities,
    ListSocialIdentitiesHandlerProtocol,
    SocialIdentityView,
)
from auth_api.internal.ports.output.uow import UnitOfWork


class ListSocialIdentitiesUseCase(ListSocialIdentitiesHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: ListSocialIdentities) -> list[SocialIdentityView]:
        async with self._uow:
            await self._uow.users.get_user_by_id(query.user_id)
            identities = await self._uow.social_identities.list_by_user_id(
                query.user_id
            )

        return [
            SocialIdentityView(
                provider=identity.provider,
                subject=identity.subject,
                email=identity.email,
                email_verified=identity.email_verified,
                created_at=identity.created_at,
            )
            for identity in identities
        ]
