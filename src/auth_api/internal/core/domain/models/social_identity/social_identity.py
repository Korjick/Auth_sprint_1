import datetime
import uuid

from auth_api.internal.pkg.domain import BaseEntity
from auth_api.internal.pkg.errors import ParamEmptyError

PROVIDER_MAX_LENGTH = 32
SUBJECT_MAX_LENGTH = 255
EMAIL_MAX_LENGTH = 255


class SocialIdentity(BaseEntity[uuid.UUID]):
    def __init__(
            self,
            oid: uuid.UUID,
            user_id: uuid.UUID,
            provider: str,
            subject: str,
            created_at: datetime.datetime,
            email: str | None = None,
            email_verified: bool = False
    ):
        provider_normalized = provider.strip().lower()
        if not provider_normalized:
            raise ParamEmptyError(param="provider")
        if len(provider_normalized) > PROVIDER_MAX_LENGTH:
            raise ValueError(
                f"provider must be <= {PROVIDER_MAX_LENGTH} chars"
            )

        subject_normalized = subject.strip()
        if not subject_normalized:
            raise ParamEmptyError(param="subject")
        if len(subject_normalized) > SUBJECT_MAX_LENGTH:
            raise ValueError(
                f"subject must be <= {SUBJECT_MAX_LENGTH} chars"
            )

        if user_id is None:
            raise ParamEmptyError(param="user_id")

        if email is not None:
            email_normalized = email.strip()
            if len(email_normalized) > EMAIL_MAX_LENGTH:
                raise ValueError(
                    f"email must be <= {EMAIL_MAX_LENGTH} chars"
                )
            email = email_normalized or None

        super().__init__(oid)
        self.user_id = user_id
        self.provider = provider_normalized
        self.subject = subject_normalized
        self.email = email
        self.email_verified = email_verified
        self.created_at = created_at
