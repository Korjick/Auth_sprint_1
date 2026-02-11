from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from internal.adapters.input.http.dependencies import admin_only
from internal.adapters.input.http.v1.role.dependencies import (
    create_role_handler,
    update_role_handler,
    delete_role_handler,
    list_roles_handler,
)
from internal.adapters.input.http.v1.role.schemas import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleResponse,
)
from internal.ports.input.role.create_role_handler import (
    CreateRole,
    CreateRoleHandlerProtocol,
)
from internal.ports.input.role.update_role_handler import (
    UpdateRole,
    UpdateRoleHandlerProtocol,
)
from internal.ports.input.role.delete_role_handler import (
    DeleteRole,
    DeleteRoleHandlerProtocol,
)
from internal.ports.input.role.list_roles_handler import (
    ListRoles,
    ListRolesHandlerProtocol,
)
from internal.ports.output.token_provider import DecodedTokenData

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
        role_request: RoleCreateRequest,
        handler: Annotated[
            CreateRoleHandlerProtocol, Depends(create_role_handler)
        ],
        _: Annotated[DecodedTokenData, Depends(admin_only)],
) -> RoleResponse:
    role = await handler.handle(CreateRole(name=role_request.name))
    return RoleResponse(id=role.id, name=role.name)


@router.get("", response_model=list[RoleResponse])
async def list_roles(
        handler: Annotated[
            ListRolesHandlerProtocol, Depends(list_roles_handler)
        ],
        _: Annotated[DecodedTokenData, Depends(admin_only)],
) -> list[RoleResponse]:
    roles = await handler.handle(ListRoles())
    return [RoleResponse(id=role.id, name=role.name) for role in roles]


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
        role_id: UUID,
        role_request: RoleUpdateRequest,
        handler: Annotated[
            UpdateRoleHandlerProtocol, Depends(update_role_handler)
        ],
        _: Annotated[DecodedTokenData, Depends(admin_only)],
) -> RoleResponse:
    role = await handler.handle(
        UpdateRole(role_id=role_id, name=role_request.name)
    )
    return RoleResponse(id=role.id, name=role.name)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
        role_id: UUID,
        handler: Annotated[
            DeleteRoleHandlerProtocol, Depends(delete_role_handler)
        ],
        _: Annotated[DecodedTokenData, Depends(admin_only)],
) -> None:
    await handler.handle(DeleteRole(role_id=role_id))
