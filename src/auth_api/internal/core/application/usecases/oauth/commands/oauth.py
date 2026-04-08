import json
import secrets
import uuid
from dataclasses import dataclass

from auth_api.internal.core.application.services.token_pair import \
    TokenPairService
from auth_api.internal.core.domain.models.session.session import Session
from auth_api.internal.core.domain.models.social_identity.social_identity import (
    SocialIdentity,
)
from auth_api.internal.core.domain.models.user.user import User
from auth_api.internal.pkg.errors import UnauthorizedError
from auth_api.internal.pkg.errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from auth_api.internal.ports.input.oauth.oauth_handler import (
    CompleteOAuth,
    LinkedSocialIdentity,
    OAuthCompleted,
    OAuthHandlerProtocol,
    StartOAuthLink,
    StartedOAuth, Flow,
)
from auth_api.internal.ports.output.cache_provider import CacheProvider
from auth_api.internal.ports.output.hash_provider import HashProvider
from auth_api.internal.ports.output.session_repository import SessionCreate
from auth_api.internal.ports.output.social_auth_provider import (
    SocialAuthProfile,
    SocialAuthProvider,
)
from auth_api.internal.ports.output.social_identity_repository import (
    SocialIdentityCreate,
)
from auth_api.internal.ports.output.uow import UnitOfWork
from auth_api.internal.ports.output.user_repository import UserCreate

RANDOM_PASSWORD_LENGTH = 32
DEFAULT_FIRST_NAME = "OAuth"
DEFAULT_LAST_NAME = "User"
STATE_KEY_NAMESPACE = "oauth"
STATE_TOKEN_LENGTH = 32
STATE_BINDING_FIELD = "state_binding"


@dataclass(frozen=True, kw_only=True)
class OAuthStatePayload:
    flow: Flow
    state_binding: str
    user_id: uuid.UUID | None = None


class OAuthUseCase(OAuthHandlerProtocol):
    def __init__(
            self,
            cache_provider: CacheProvider,
            social_auth_provider: SocialAuthProvider,
            uow: UnitOfWork,
            hash_provider: HashProvider,
            token_pair_service: TokenPairService,
            state_ttl_sec: int,
    ) -> None:
        self._cache = cache_provider
        self._provider = social_auth_provider
        self._uow = uow
        self._hasher = hash_provider
        self._token_pair_service = token_pair_service
        self._state_ttl_sec = state_ttl_sec

    async def start_login(self) -> StartedOAuth:
        state = self._generate_state_token()
        state_binding = self._generate_state_token()
        payload = json.dumps(
            {
                "flow": Flow.LOGIN,
                STATE_BINDING_FIELD: state_binding,
            }
        )
        await self._cache.cache_data(
            key=self._get_cache_state_key(state),
            data=payload,
            expire_sec=self._state_ttl_sec,
        )
        return StartedOAuth(
            authorization_url=self._provider.build_authorization_url(
                state=state
            ),
            state_binding=state_binding,
        )

    async def start_link(self, command: StartOAuthLink) -> StartedOAuth:
        state = self._generate_state_token()
        state_binding = self._generate_state_token()
        payload = json.dumps(
            {
                "flow": Flow.LINK,
                STATE_BINDING_FIELD: state_binding,
                "user_id": str(command.user_id),
            }
        )
        await self._cache.cache_data(
            key=self._get_cache_state_key(state),
            data=payload,
            expire_sec=self._state_ttl_sec,
        )
        return StartedOAuth(
            authorization_url=self._provider.build_authorization_url(
                state=state
            ),
            state_binding=state_binding,
        )

    async def complete(self, command: CompleteOAuth) -> OAuthCompleted:
        code = command.code.strip()
        state = command.state.strip()
        state_binding = (
            command.state_binding.strip()
            if command.state_binding is not None
            else ""
        )
        device_fingerprint = command.device_fingerprint.strip()
        if not code or not state or not state_binding or not device_fingerprint:
            raise UnauthorizedError()

        state_payload = await self._get_state_payload(state, state_binding)
        profile = await self._provider.exchange_code(code=code)

        if state_payload.flow == Flow.LINK:
            if state_payload.user_id is None:
                raise UnauthorizedError()
            return await self._handle_link(
                profile=profile,
                user_id=state_payload.user_id,
            )

        return await self._handle_login(
            profile=profile,
            device_fingerprint=device_fingerprint,
        )

    async def _handle_login(
            self,
            profile: SocialAuthProfile,
            device_fingerprint: str,
    ) -> OAuthCompleted:
        async with self._uow:
            user = await self._resolve_login_user(profile)
            token_pair = self._token_pair_service.create_for_user(user)

            await self._upsert_user_session(
                user_id=user.id,
                device_fingerprint=device_fingerprint,
                refresh_jti=token_pair.refresh_token.jti,
                refresh_exp=token_pair.refresh_token.exp,
            )
            await self._uow.commit()

        return OAuthCompleted(
            flow=Flow.LOGIN,
            access_session=token_pair.access_token.token,
            refresh_session=token_pair.refresh_token.token,
        )

    async def _resolve_login_user(self, profile: SocialAuthProfile) -> User:
        try:
            identity = await self._uow.social_identities.get_by_provider_subject(
                provider=profile.provider,
                subject=profile.subject,
            )
            return await self._uow.users.get_user_by_id(identity.user_id)
        except EntityNotFoundError:
            return await self._create_user_with_identity(profile)

    async def _create_user_with_identity(
            self,
            profile: SocialAuthProfile,
    ) -> User:
        login = self._build_login(profile)

        try:
            await self._uow.users.get_user_by_login(login=login)
        except EntityNotFoundError:
            pass
        else:
            raise EntityAlreadyExistsError(param="login", key=login)

        user = await self._uow.users.save_user(
            UserCreate(
                login=login,
                password_hash=self._hasher.hash_data(
                    secrets.token_urlsafe(RANDOM_PASSWORD_LENGTH),
                ),
                first_name=profile.first_name
                if profile.first_name
                else DEFAULT_FIRST_NAME,
                last_name=profile.last_name
                if profile.last_name
                else DEFAULT_LAST_NAME,
                is_active=True,
            )
        )

        await self._uow.social_identities.create_identity(
            SocialIdentityCreate(
                user_id=user.id,
                provider=profile.provider,
                subject=profile.subject,
                email=profile.email,
                email_verified=profile.email_verified,
            )
        )
        return user

    async def _upsert_user_session(
            self,
            *,
            user_id: uuid.UUID,
            device_fingerprint: str,
            refresh_jti: uuid.UUID,
            refresh_exp,
    ) -> None:
        sessions = await self._uow.sessions.get_sessions_by_user_id(
            user_id=user_id)
        existing = next(
            (
                session
                for session in sessions
                if session.device_fingerprint == device_fingerprint
            ),
            None,
        )

        if existing is None:
            await self._uow.sessions.create_session(
                SessionCreate(
                    user_id=user_id,
                    device_fingerprint=device_fingerprint,
                    expires_at=refresh_exp,
                    jti=refresh_jti,
                )
            )
            return

        await self._uow.sessions.update_session(
            Session(
                oid=existing.id,
                user_id=existing.user_id,
                jti=refresh_jti,
                device_fingerprint=existing.device_fingerprint,
                expire_at=refresh_exp,
            )
        )

    async def _handle_link(
            self,
            profile: SocialAuthProfile,
            user_id: uuid.UUID,
    ) -> OAuthCompleted:
        async with self._uow:
            await self._uow.users.get_user_by_id(user_id)

            existing = await self._find_identity_by_provider_subject(profile)
            if existing is not None:
                if existing.user_id != user_id:
                    raise EntityAlreadyExistsError(
                        param="provider_subject",
                        key=f"{profile.provider}:{profile.subject}",
                    )
                return OAuthCompleted(
                    flow=Flow.LINK,
                    identity=self._to_linked_identity(existing),
                )

            existing_provider = await self._find_identity_by_user_provider(
                user_id=user_id,
                provider=profile.provider,
            )
            if existing_provider is not None:
                if existing_provider.subject != profile.subject:
                    raise EntityAlreadyExistsError(
                        param="user_provider",
                        key=f"{user_id}:{profile.provider}",
                    )
                return OAuthCompleted(
                    flow=Flow.LINK,
                    identity=self._to_linked_identity(existing_provider),
                )

            created = await self._uow.social_identities.create_identity(
                SocialIdentityCreate(
                    user_id=user_id,
                    provider=profile.provider,
                    subject=profile.subject,
                    email=profile.email,
                    email_verified=profile.email_verified,
                )
            )
            await self._uow.commit()

        return OAuthCompleted(
            flow=Flow.LINK,
            identity=self._to_linked_identity(created),
        )

    async def _find_identity_by_provider_subject(
            self,
            profile: SocialAuthProfile,
    ) -> SocialIdentity | None:
        try:
            return await self._uow.social_identities.get_by_provider_subject(
                provider=profile.provider,
                subject=profile.subject,
            )
        except EntityNotFoundError:
            return None

    async def _find_identity_by_user_provider(
            self,
            *,
            user_id: uuid.UUID,
            provider: str,
    ) -> SocialIdentity | None:
        try:
            return await self._uow.social_identities.get_by_user_provider(
                user_id=user_id,
                provider=provider,
            )
        except EntityNotFoundError:
            return None

    async def _get_state_payload(
            self,
            state: str,
            expected_state_binding: str,
    ) -> OAuthStatePayload:
        raw = await self._cache.pop_from_cache(
            self._get_cache_state_key(state))
        if not isinstance(raw, str) or not raw:
            raise UnauthorizedError()

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise UnauthorizedError() from exc

        if not isinstance(payload, dict):
            raise UnauthorizedError()

        raw_flow = payload.get("flow")
        if not isinstance(raw_flow, str):
            raise UnauthorizedError()
        try:
            flow = Flow(raw_flow)
        except ValueError as exc:
            raise UnauthorizedError() from exc

        raw_state_binding = payload.get(STATE_BINDING_FIELD)
        if not isinstance(raw_state_binding, str) or not raw_state_binding:
            raise UnauthorizedError()
        if raw_state_binding != expected_state_binding:
            raise UnauthorizedError()

        user_id: uuid.UUID | None = None
        if flow == Flow.LINK:
            raw_user_id = payload.get("user_id")
            if not isinstance(raw_user_id, str) or not raw_user_id.strip():
                raise UnauthorizedError()
            try:
                user_id = uuid.UUID(raw_user_id)
            except ValueError as exc:
                raise UnauthorizedError() from exc

        return OAuthStatePayload(
            flow=flow,
            state_binding=raw_state_binding,
            user_id=user_id,
        )

    def _get_cache_state_key(self, state: str) -> str:
        provider_key = self._provider.name.strip().lower()
        return f"{STATE_KEY_NAMESPACE}:{provider_key}:state:{state}"

    @staticmethod
    def _generate_state_token() -> str:
        return secrets.token_urlsafe(STATE_TOKEN_LENGTH)

    @staticmethod
    def _to_linked_identity(identity: SocialIdentity) -> LinkedSocialIdentity:
        return LinkedSocialIdentity(
            provider=identity.provider,
            subject=identity.subject,
            email=identity.email,
            email_verified=identity.email_verified,
            created_at=identity.created_at,
        )

    @staticmethod
    def _build_login(profile: SocialAuthProfile) -> str:
        provider = profile.provider.strip().lower()
        subject = profile.subject.strip()
        return f"{provider}_{subject}"
