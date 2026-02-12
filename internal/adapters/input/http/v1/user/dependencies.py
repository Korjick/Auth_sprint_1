from fastapi import Depends

from internal.adapters.input.dependencies import (
    get_uow,
    get_hash_provider,
    get_token_provider,
    get_time_provider,
)
from internal.core.application.usecases.user.commands.login_user import \
    LoginUserUseCase
from internal.core.application.usecases.user.commands.create_user import \
    CreateUserUseCase
from internal.core.application.usecases.user.commands.logout_user import \
    LogoutUserUseCase
from internal.core.application.usecases.user.commands.logout_all import \
    LogoutAllUseCase
from internal.core.application.usecases.user.commands.update_user import \
    UpdateUserUseCase
from internal.core.application.usecases.user.commands.assign_role import \
    AssignRoleUseCase
from internal.core.application.usecases.user.commands.remove_role import \
    RemoveRoleUseCase
from internal.core.application.usecases.user.commands.refresh_session import \
    RefreshSessionUseCase
from internal.core.application.services.token_pair import \
    TokenPairService
from internal.core.application.usecases.user.queries.get_user_by_login import \
    GetUserByLoginUseCase
from internal.core.application.usecases.user.queries.get_login_history import \
    GetLoginHistoryUseCase
from internal.ports.input.user.create_user_handler import \
    CreateUserHandlerProtocol
from internal.ports.input.user.get_user_by_login_handler import \
    GetUserByLoginHandlerProtocol
from internal.ports.input.user.login_user_handler import \
    LoginUserHandlerProtocol
from internal.ports.input.user.logout_user_handler import \
    LogoutHandlerProtocol
from internal.ports.input.user.refresh_session_handler import \
    RefreshSessionHandlerProtocol
from internal.ports.input.user.logout_all_handler import \
    LogoutAllHandlerProtocol
from internal.ports.input.user.update_user_handler import \
    UpdateUserHandlerProtocol
from internal.ports.input.user.get_login_history_handler import \
    GetLoginHistoryHandlerProtocol
from internal.ports.input.user.assign_role_handler import \
    AssignRoleHandlerProtocol
from internal.ports.input.user.remove_role_handler import \
    RemoveRoleHandlerProtocol
from internal.ports.output.hash_provider import HashProvider
from internal.ports.output.time_provider import TimeProvider
from internal.ports.output.token_provider import TokenProvider
from internal.ports.output.uow import UnitOfWork


def create_user_handler(
        uow: UnitOfWork = Depends(get_uow),
        password_hasher: HashProvider = Depends(get_hash_provider),
) -> CreateUserHandlerProtocol:
    return CreateUserUseCase(uow, password_hasher)


def get_user_by_login_handler(
        uow: UnitOfWork = Depends(get_uow),
) -> GetUserByLoginHandlerProtocol:
    return GetUserByLoginUseCase(uow)


def get_token_pair_service(
        token_provider: TokenProvider = Depends(get_token_provider)) \
        -> TokenPairService:
    return TokenPairService(token_provider)


def login_user_handler(
        uow: UnitOfWork = Depends(get_uow),
        password_hasher: HashProvider = Depends(get_hash_provider),
        token_pair_service: TokenPairService = Depends(get_token_pair_service)
) -> LoginUserHandlerProtocol:
    return LoginUserUseCase(uow, password_hasher, token_pair_service)


def refresh_session_handler(
        uow: UnitOfWork = Depends(get_uow),
        token_pair_service: TokenPairService = Depends(get_token_pair_service),
        time_provider: TimeProvider = Depends(get_time_provider),
) -> RefreshSessionHandlerProtocol:
    return RefreshSessionUseCase(
        token_pair_service, uow, time_provider
    )


def logout_handler(
        uow: UnitOfWork = Depends(get_uow),
        token_provider: TokenProvider = Depends(get_token_provider),
) -> LogoutHandlerProtocol:
    return LogoutUserUseCase(uow, token_provider)


def logout_all_handler(
    uow: UnitOfWork = Depends(get_uow),
    token_provider: TokenProvider = Depends(get_token_provider),
) -> LogoutAllHandlerProtocol:
    return LogoutAllUseCase(uow, token_provider)


def update_user_handler(
    uow: UnitOfWork = Depends(get_uow),
    hash_provider: HashProvider = Depends(get_hash_provider),
) -> UpdateUserHandlerProtocol:
    return UpdateUserUseCase(uow, hash_provider)


def get_login_history_handler(
    uow: UnitOfWork = Depends(get_uow),
) -> GetLoginHistoryHandlerProtocol:
    return GetLoginHistoryUseCase(uow)


def assign_role_handler(
    uow: UnitOfWork = Depends(get_uow),
) -> AssignRoleHandlerProtocol:
    return AssignRoleUseCase(uow)


def remove_role_handler(
    uow: UnitOfWork = Depends(get_uow),
) -> RemoveRoleHandlerProtocol:
    return RemoveRoleUseCase(uow)
