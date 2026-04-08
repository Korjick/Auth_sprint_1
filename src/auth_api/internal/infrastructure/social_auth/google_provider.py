import asyncio
import json
from dataclasses import dataclass
from http import HTTPMethod
from urllib import error as url_error
from urllib import parse as url_parse
from urllib import request as url_request

import jwt

from auth_api.internal.pkg.errors import (
    FeatureDisabledError,
    InfrastructureError,
    UnauthorizedError,
)
from auth_api.internal.ports.output.social_auth_provider import (
    SocialAuthProfile,
    SocialAuthProvider,
)

GOOGLE_PROVIDER_NAME = "google"
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401


@dataclass(kw_only=True)
class GoogleOAuthConfig:
    enabled: bool
    client_id: str
    client_secret: str
    redirect_uri: str
    authorize_url: str
    token_url: str
    jwks_url: str
    scopes: str
    issuer_primary: str
    issuer_secondary: str
    http_timeout_sec: float


class GoogleSocialAuthProvider(SocialAuthProvider):
    def __init__(self, config: GoogleOAuthConfig):
        self._config = config
        self._jwks_client = jwt.PyJWKClient(config.jwks_url)

    @property
    def name(self) -> str:
        return GOOGLE_PROVIDER_NAME

    def build_authorization_url(
            self,
            *,
            state: str,
    ) -> str:
        self._ensure_configured()

        params = {
            "client_id": self._config.client_id,
            "redirect_uri": self._config.redirect_uri,
            "response_type": "code",
            "scope": self._config.scopes,
            "state": state,
        }
        return f"{self._config.authorize_url}?{url_parse.urlencode(params)}"

    async def exchange_code(
            self,
            *,
            code: str,
    ) -> SocialAuthProfile:
        self._ensure_configured()

        token_response = await asyncio.to_thread(
            self._exchange_code_sync,
            code,
        )
        id_token = token_response.get("id_token")
        if not isinstance(id_token, str) or not id_token:
            raise UnauthorizedError()

        claims = await asyncio.to_thread(
            self._validate_id_token_sync,
            id_token,
        )

        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise UnauthorizedError()

        email = claims.get("email")
        if not isinstance(email, str):
            email = None

        email_verified_value = claims.get("email_verified", False)
        email_verified = (
            email_verified_value is True
            or (
                isinstance(email_verified_value, str)
                and email_verified_value.lower() == "true"
            )
        )

        first_name = claims.get("given_name")
        if not isinstance(first_name, str):
            first_name = None

        last_name = claims.get("family_name")
        if not isinstance(last_name, str):
            last_name = None

        return SocialAuthProfile(
            provider=self.name,
            subject=subject,
            email=email,
            email_verified=email_verified,
            first_name=first_name,
            last_name=last_name,
        )

    def _ensure_configured(self) -> None:
        if not self._config.enabled:
            raise FeatureDisabledError(feature="google_oauth")
        if not self._config.client_id:
            raise InfrastructureError(service="google_oauth")
        if not self._config.client_secret:
            raise InfrastructureError(service="google_oauth")
        if not self._config.redirect_uri:
            raise InfrastructureError(service="google_oauth")

    def _exchange_code_sync(
            self,
            code: str,
    ) -> dict[str, object]:
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
            "redirect_uri": self._config.redirect_uri,
        }
        encoded = url_parse.urlencode(payload).encode("utf-8")
        request = url_request.Request(
            url=self._config.token_url,
            data=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method=HTTPMethod.POST.value,
        )
        try:
            with url_request.urlopen(
                    request,
                    timeout=self._config.http_timeout_sec,
            ) as response:
                raw = response.read()
        except url_error.HTTPError as exc:
            if exc.code in {HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED}:
                raise UnauthorizedError() from exc
            raise InfrastructureError(service="google_oauth", cause=exc) from exc
        except url_error.URLError as exc:
            raise InfrastructureError(service="google_oauth", cause=exc) from exc

        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InfrastructureError(service="google_oauth", cause=exc) from exc

        if not isinstance(decoded, dict):
            raise InfrastructureError(service="google_oauth")
        return decoded

    def _validate_id_token_sync(
            self,
            id_token: str,
    ) -> dict[str, object]:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(id_token).key
            claims = jwt.decode(
                id_token,
                signing_key,
                algorithms=["RS256"],
                audience=self._config.client_id,
                options={"require": ["iss", "aud", "sub", "exp"]},
            )
        except jwt.PyJWTError as exc:
            raise UnauthorizedError() from exc

        issuer = claims.get("iss")
        if issuer not in {
            self._config.issuer_primary,
            self._config.issuer_secondary,
        }:
            raise UnauthorizedError()

        return claims
