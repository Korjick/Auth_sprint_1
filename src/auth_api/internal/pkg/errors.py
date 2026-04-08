from typing import Any, Optional


class BaseAppError(Exception):
    """Базовый класс для всех ошибок приложения.

    Каждая ошибка имеет:
    - code: уникальный строковый код для идентификации и перевода на клиенте
    - message: человекочитаемое описание
    - details: дополнительные данные (параметры, значения и т.д.)
    """

    code: str = "INTERNAL_ERROR"

    def __init__(self, **details: Any) -> None:
        self.details: dict[str, Any] = details
        super().__init__(self.get_message())

    def get_message(self) -> str:
        return "unexpected application error"

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "code": self.code,
            "message": self.get_message(),
        }
        if self.details:
            result["details"] = self.details
        return result


# Validation errors

class ValidationError(BaseAppError):
    code = "VALIDATION_ERROR"

    def get_message(self) -> str:
        return "validation error"


class ParamEmptyError(ValidationError):
    code = "VALIDATION_PARAM_EMPTY"

    def __init__(self, param: str) -> None:
        self.param = param
        super().__init__(param=param)

    def get_message(self) -> str:
        return f"{self.param} must not be empty"


# Entity errors

class EntityNotFoundError(BaseAppError):
    code = "ENTITY_NOT_FOUND"

    def __init__(self,
                 param: str,
                 key: str,
                 cause: Optional[Exception] = None):
        self.key = key
        self.param = param
        self.cause = cause
        super().__init__(param=param, key=key)

    def get_message(self) -> str:
        return f"entity not found (key: {self.key} - param: {self.param})"


class EntityAlreadyExistsError(BaseAppError):
    code = "ENTITY_ALREADY_EXISTS"

    def __init__(self,
                 param: str,
                 key: str):
        self.param = param
        self.key = key
        super().__init__(param=param, key=key)

    def get_message(self) -> str:
        return f"entity already exists (key: {self.key} - param: {self.param})"


# Auth errors

class InvalidCredentialsError(BaseAppError):
    code = "INVALID_CREDENTIALS"

    def get_message(self) -> str:
        return "invalid login or password"


class UnauthorizedError(BaseAppError):
    code = "UNAUTHORIZED"

    def get_message(self) -> str:
        return "user is not authorized"


class ForbiddenError(BaseAppError):
    code = "FORBIDDEN"

    def get_message(self) -> str:
        return "access to resource is forbidden"


class FeatureDisabledError(ValidationError):
    code = "FEATURE_DISABLED"

    def __init__(self, feature: str) -> None:
        self.feature = feature
        super().__init__(feature=feature)

    def get_message(self) -> str:
        return f"{self.feature} is disabled"


class RateLimitExceededError(BaseAppError):
    code = "RATE_LIMIT_EXCEEDED"

    def __init__(
            self,
            limit: int,
            retry_after: int,
            reset_at: int,
            bucket: str,
    ) -> None:
        super().__init__(
            limit=limit,
            remaining=0,
            retry_after=retry_after,
            reset_at=reset_at,
            bucket=bucket,
        )

    def get_message(self) -> str:
        return "too many requests"


# Database / infrastructure errors

class DatabaseError(BaseAppError):
    code = "DATABASE_ERROR"

    def __init__(self, cause: Exception | None = None):
        self.cause = cause
        super().__init__(
            operation=type(cause).__name__ if cause else "unknown")

    def get_message(self) -> str:
        return "a database error occurred"


class InfrastructureError(BaseAppError):
    code = "INFRASTRUCTURE_ERROR"

    def __init__(self, service: str, cause: Exception | None = None):
        self.service = service
        self.cause = cause
        super().__init__(
            service=service,
            operation=type(cause).__name__ if cause else "unknown")

    def get_message(self) -> str:
        return "an infrastructure error occurred"
