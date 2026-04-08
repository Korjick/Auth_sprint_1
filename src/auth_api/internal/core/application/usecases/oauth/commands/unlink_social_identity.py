from auth_api.internal.pkg.errors import ParamEmptyError
from auth_api.internal.ports.input.oauth.unlink_social_identity_handler import (
    UnlinkSocialIdentity,
    UnlinkSocialIdentityHandlerProtocol,
)
from auth_api.internal.ports.output.uow import UnitOfWork


class UnlinkSocialIdentityUseCase(UnlinkSocialIdentityHandlerProtocol):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: UnlinkSocialIdentity) -> None:
        provider = command.provider.strip().lower()
        if not provider:
            raise ParamEmptyError(param="provider")

        async with self._uow:
            await self._uow.users.get_user_by_id(command.user_id)
            await self._uow.social_identities.get_by_user_provider(
                user_id=command.user_id,
                provider=provider,
            )
            await self._uow.social_identities.delete_by_user_provider(
                user_id=command.user_id,
                provider=provider,
            )
            await self._uow.commit()
