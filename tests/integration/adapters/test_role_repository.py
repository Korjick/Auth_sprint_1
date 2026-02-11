import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text

from internal.adapters.output.postgres.role.repository import (
    PostgresRoleRepository,
)
from internal.core.domain.models.role.role import ADMIN_ROLE_NAME
from internal.ports.output.role_repository import RoleCreate
from internal.pkg.errors import EntityNotFoundError, ForbiddenError


@pytest_asyncio.fixture
async def role_repo(db_session):
    """Репозиторий ролей с тестовой сессией."""
    return PostgresRoleRepository(db_session)


@pytest_asyncio.fixture(autouse=True)
async def _clean_roles(db_session):
    """Очистка таблиц ролей перед каждым тестом."""
    yield
    await db_session.execute(text("DELETE FROM service.user_roles"))
    await db_session.execute(text("DELETE FROM service.roles"))
    await db_session.commit()


class TestCreateRole:
    """Тесты создания роли."""

    @pytest.mark.asyncio
    async def test_create_role_returns_domain_role(self, role_repo):
        """create_role возвращает доменную модель Role."""
        role = await role_repo.create_role(RoleCreate(name="editor"))

        assert role.name == "editor"
        assert isinstance(role.id, uuid.UUID)

    @pytest.mark.asyncio
    async def test_create_admin_role(self, role_repo):
        """Создание роли admin проходит успешно."""
        role = await role_repo.create_role(
            RoleCreate(name=ADMIN_ROLE_NAME))
        assert role.name == ADMIN_ROLE_NAME


class TestListRoles:
    """Тесты получения списка ролей."""

    @pytest.mark.asyncio
    async def test_list_roles_empty(self, role_repo):
        """Пустой список ролей."""
        roles = await role_repo.list_roles()
        assert roles == []

    @pytest.mark.asyncio
    async def test_list_roles_returns_all(self, role_repo):
        """list_roles возвращает все созданные роли."""
        await role_repo.create_role(RoleCreate(name="role1"))
        await role_repo.create_role(RoleCreate(name="role2"))

        roles = await role_repo.list_roles()
        names = {r.name for r in roles}
        assert names == {"role1", "role2"}


class TestGetRoleById:
    """Тесты получения роли по id."""

    @pytest.mark.asyncio
    async def test_get_existing_role(self, role_repo):
        """Существующая роль возвращается по id."""
        created = await role_repo.create_role(RoleCreate(name="viewer"))
        found = await role_repo.get_role_by_id(created.id)

        assert found.id == created.id
        assert found.name == "viewer"

    @pytest.mark.asyncio
    async def test_get_nonexistent_role(self, role_repo):
        """Несуществующая роль вызывает EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await role_repo.get_role_by_id(uuid.uuid4())


class TestUpdateRole:
    """Тесты обновления роли."""

    @pytest.mark.asyncio
    async def test_update_role_name(self, role_repo):
        """Имя роли обновляется корректно."""
        role = await role_repo.create_role(RoleCreate(name="oldname"))
        updated = await role_repo.update_role(role.id, "newname")

        assert updated.name == "newname"
        assert updated.id == role.id

    @pytest.mark.asyncio
    async def test_update_nonexistent_role(self, role_repo):
        """Обновление несуществующей роли вызывает EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await role_repo.update_role(uuid.uuid4(), "newname")

    @pytest.mark.asyncio
    async def test_update_admin_role_raises_forbidden(self, role_repo):
        """Обновление admin-роли вызывает ForbiddenError."""
        admin = await role_repo.create_role(
            RoleCreate(name=ADMIN_ROLE_NAME))
        with pytest.raises(ForbiddenError):
            await role_repo.update_role(admin.id, "renamed")


class TestDeleteRole:
    """Тесты удаления роли."""

    @pytest.mark.asyncio
    async def test_delete_role_success(self, role_repo):
        """Роль удаляется из БД."""
        role = await role_repo.create_role(RoleCreate(name="todelete"))
        await role_repo.delete_role(role.id)

        with pytest.raises(EntityNotFoundError):
            await role_repo.get_role_by_id(role.id)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_role(self, role_repo):
        """Удаление несуществующей роли вызывает EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await role_repo.delete_role(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_delete_admin_role_raises_forbidden(self, role_repo):
        """Удаление admin-роли вызывает ForbiddenError."""
        admin = await role_repo.create_role(
            RoleCreate(name=ADMIN_ROLE_NAME))
        with pytest.raises(ForbiddenError):
            await role_repo.delete_role(admin.id)
