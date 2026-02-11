from fastapi import Depends

from internal.adapters.input.dependencies import get_uow
from internal.core.application.usecases.role.commands.create_role import \
    CreateRoleUseCase
from internal.core.application.usecases.role.commands.update_role import \
    UpdateRoleUseCase
from internal.core.application.usecases.role.commands.delete_role import \
    DeleteRoleUseCase
from internal.core.application.usecases.role.queries.list_roles import \
    ListRolesUseCase
from internal.ports.input.role.create_role_handler import \
    CreateRoleHandlerProtocol
from internal.ports.input.role.update_role_handler import \
    UpdateRoleHandlerProtocol
from internal.ports.input.role.delete_role_handler import \
    DeleteRoleHandlerProtocol
from internal.ports.input.role.list_roles_handler import \
    ListRolesHandlerProtocol
from internal.ports.output.uow import UnitOfWork


def create_role_handler(
        uow: UnitOfWork = Depends(get_uow),
) -> CreateRoleHandlerProtocol:
    return CreateRoleUseCase(uow)


def update_role_handler(
        uow: UnitOfWork = Depends(get_uow),
) -> UpdateRoleHandlerProtocol:
    return UpdateRoleUseCase(uow)


def delete_role_handler(
        uow: UnitOfWork = Depends(get_uow),
) -> DeleteRoleHandlerProtocol:
    return DeleteRoleUseCase(uow)


def list_roles_handler(
        uow: UnitOfWork = Depends(get_uow),
) -> ListRolesHandlerProtocol:
    return ListRolesUseCase(uow)
