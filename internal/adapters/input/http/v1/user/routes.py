from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from internal.adapters.input.http.dependencies import (
    admin_only,
    refresh_token_required,
    access_token_required,
    get_device_fingerprint,
)
from internal.adapters.input.http.v1.user.dependencies import (
    create_user_handler,
    get_user_by_id_handler,
    login_user_handler,
    logout_handler,
    refresh_session_handler,
    update_user_handler,
    logout_all_handler,
    get_login_history_handler,
    assign_role_handler,
    remove_role_handler,
)
from internal.adapters.input.http.v1.user.schemas import (
    UserCreateRequest,
    UserCreateResponse,
    UserDetailResponse,
    UserLoginRequest,
    UserLoginResponse,
    RefreshTokenResponse,
    UserUpdateRequest,
    SessionHistoryResponse,
    RoleAssignRequest,
    UserRoleResponse,
)
from internal.ports.input.user.create_user_handler import (
    CreateUser,
    CreateUserHandlerProtocol,
)
from internal.ports.input.user.get_user_by_id_handler import (
    GetUserById,
    GetUserByIdHandlerProtocol,
)
from internal.ports.input.user.login_user_handler import \
    LoginUserHandlerProtocol, LoginUser
from internal.ports.input.user.logout_user_handler import (
    Logout,
    LogoutHandlerProtocol,
)
from internal.ports.input.user.logout_all_handler import (
    LogoutAll,
    LogoutAllHandlerProtocol,
)
from internal.ports.input.user.update_user_handler import (
    UpdateUser,
    UpdateUserHandlerProtocol,
)
from internal.ports.input.user.get_login_history_handler import (
    GetLoginHistory,
    GetLoginHistoryHandlerProtocol,
)
from internal.ports.input.user.assign_role_handler import (
    AssignRole,
    AssignRoleHandlerProtocol,
)
from internal.ports.input.user.remove_role_handler import (
    RemoveRole,
    RemoveRoleHandlerProtocol,
)
from internal.ports.input.user.refresh_session_handler import (
    RefreshSession,
    RefreshSessionHandlerProtocol,
)
from internal.ports.output.token_provider import DecodedTokenData

router = APIRouter(prefix='/user', tags=['Users'])


@router.post(
    '/signup',
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
        # params
        user_create_request: UserCreateRequest,
        # deps
        create_user_handler: Annotated[
            CreateUserHandlerProtocol, Depends(create_user_handler)
        ],
) -> UserCreateResponse:
    command = CreateUser(
        login=user_create_request.login,
        password=user_create_request.password,
        first_name=user_create_request.first_name,
        last_name=user_create_request.last_name,
    )
    user = await create_user_handler.handle(command)
    return UserCreateResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
    )


@router.post('/login', response_model=UserLoginResponse)
async def login_user(
        # params
        user_login_request: UserLoginRequest,
        # deps
        user_login_handler: Annotated[
            LoginUserHandlerProtocol, Depends(login_user_handler)
        ],
        device_fingerprint: Annotated[
            str, Depends(get_device_fingerprint)
        ]
):
    data = await user_login_handler.handle(
        LoginUser(login=user_login_request.login,
                  password=user_login_request.password,
                  device_fingerprint=device_fingerprint))
    return UserLoginResponse(access_token=data.access_session,
                             refresh_token=data.refresh_session)


@router.post('/refresh', response_model=RefreshTokenResponse)
async def refresh_token(
        # deps
        user_details: Annotated[
            DecodedTokenData, Depends(refresh_token_required)
        ],
        refresh_handler: Annotated[
            RefreshSessionHandlerProtocol, Depends(refresh_session_handler)
        ],
        device_fingerprint: Annotated[
            str, Depends(get_device_fingerprint)
        ]
):
    result = await refresh_handler.handle(
        RefreshSession(user=user_details.user,
                       device_fingerprint=device_fingerprint,
                       jti=user_details.jti)
    )
    return RefreshTokenResponse(access_token=result.access_session,
                                refresh_token=result.refresh_session)


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(
        logout_handler: Annotated[
            LogoutHandlerProtocol, Depends(logout_handler)
        ],
        user_details: Annotated[
            DecodedTokenData, Depends(access_token_required)
        ],
        device_fingerprint: Annotated[
            str, Depends(get_device_fingerprint)
        ],
):
    await logout_handler.handle(
        Logout(
            user_id=user_details.user.user_id,
            device_fingerprint=device_fingerprint,
            access_token_jti=user_details.jti,
        )
    )


@router.post('/logout/all', status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
        logout_all_handler: Annotated[
            LogoutAllHandlerProtocol, Depends(logout_all_handler)
        ],
        user_details: Annotated[
            DecodedTokenData, Depends(access_token_required)
        ],
):
    await logout_all_handler.handle(
        LogoutAll(user_id=user_details.user.user_id,
                  access_token_jti=user_details.jti)
    )


@router.patch('', response_model=UserDetailResponse)
async def update_user(
        user_update_request: UserUpdateRequest,
        update_handler: Annotated[
            UpdateUserHandlerProtocol, Depends(update_user_handler)
        ],
        user_details: Annotated[
            DecodedTokenData, Depends(access_token_required)
        ],
) -> UserDetailResponse:
    user = await update_handler.handle(
        UpdateUser(
            user_id=user_details.user.user_id,
            current_password=user_update_request.current_password,
            new_login=user_update_request.new_login,
            new_password=user_update_request.new_password,
        )
    )
    return UserDetailResponse(
        id=user.id,
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
    )


@router.get('/history', response_model=list[SessionHistoryResponse])
async def get_login_history(
        history_handler: Annotated[
            GetLoginHistoryHandlerProtocol, Depends(get_login_history_handler)
        ],
        user_details: Annotated[
            DecodedTokenData, Depends(access_token_required)
        ],
) -> list[SessionHistoryResponse]:
    sessions = await history_handler.handle(
        GetLoginHistory(user=user_details.user)
    )
    return [
        SessionHistoryResponse(
            id=session.id,
            device_fingerprint=session.device_fingerprint,
        )
        for session in sessions
    ]


@router.get('', response_model=UserDetailResponse)
async def get_user_info(
        # deps
        get_user_handler: Annotated[
            GetUserByIdHandlerProtocol, Depends(get_user_by_id_handler)
        ],
        user_details: Annotated[
            DecodedTokenData, Depends(access_token_required)
        ],
) -> UserDetailResponse:
    user = await get_user_handler.handle(
        GetUserById(user_id=user_details.user.user_id)
    )
    return UserDetailResponse(
        id=user.id,
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
    )


@router.post('/{user_id}/roles', response_model=UserRoleResponse)
async def assign_role(
        user_id: UUID,
        role_request: RoleAssignRequest,
        handler: Annotated[
            AssignRoleHandlerProtocol, Depends(assign_role_handler)
        ],
        _: Annotated[DecodedTokenData, Depends(admin_only)],
) -> UserRoleResponse:
    user = await handler.handle(
        AssignRole(user_id=user_id, role_id=role_request.role_id)
    )
    return UserRoleResponse(login=user.login, roles=user.roles)


@router.delete('/{user_id}/roles/{role_id}',
               response_model=UserRoleResponse)
async def remove_role(
        user_id: UUID,
        role_id: UUID,
        handler: Annotated[
            RemoveRoleHandlerProtocol, Depends(remove_role_handler)
        ],
        _: Annotated[DecodedTokenData, Depends(admin_only)],
) -> UserRoleResponse:
    user = await handler.handle(
        RemoveRole(user_id=user_id, role_id=role_id)
    )
    return UserRoleResponse(login=user.login, roles=user.roles)
