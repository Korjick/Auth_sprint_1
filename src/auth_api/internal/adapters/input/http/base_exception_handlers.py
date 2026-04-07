import logging

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from auth_api.internal.pkg.errors import (
    BaseAppError,
    ValidationError,
    EntityNotFoundError,
    EntityAlreadyExistsError,
    InvalidCredentialsError,
    UnauthorizedError,
    ForbiddenError,
    DatabaseError,
    InfrastructureError,
)

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
            request: Request, exc: EntityNotFoundError):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=exc.to_dict(),
        )

    @app.exception_handler(EntityAlreadyExistsError)
    async def already_exists_handler(
            request: Request, exc: EntityAlreadyExistsError):
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=exc.to_dict(),
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
            request: Request, exc: ValidationError):
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=exc.to_dict(),
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
            request: Request, exc: InvalidCredentialsError):
        return ORJSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=exc.to_dict(),
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(
            request: Request, exc: UnauthorizedError):
        return ORJSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=exc.to_dict(),
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(
            request: Request, exc: ForbiddenError):
        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=exc.to_dict(),
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(
            request: Request, exc: DatabaseError):
        logger.error("Database error: %s", exc.cause, exc_info=exc.cause)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=exc.to_dict(),
        )

    @app.exception_handler(InfrastructureError)
    async def infrastructure_error_handler(
            request: Request, exc: InfrastructureError):
        logger.error("Infrastructure error: %s", exc.cause, exc_info=exc.cause)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=exc.to_dict(),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
            request: Request, exc: SQLAlchemyError):
        logger.error("Unhandled SQLAlchemy error: %s", exc, exc_info=exc)
        wrapped = DatabaseError(cause=exc)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=wrapped.to_dict(),
        )

    @app.exception_handler(BaseAppError)
    async def base_app_error_handler(
            request: Request, exc: BaseAppError):
        logger.error("Unhandled app error: %s", exc, exc_info=exc)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=exc.to_dict(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
            request: Request, exc: Exception):
        logger.critical("Unhandled exception: %s", exc, exc_info=exc)
        wrapped = BaseAppError(cause=exc)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=wrapped.to_dict(),
        )

