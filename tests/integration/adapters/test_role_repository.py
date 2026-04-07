import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text

from auth_api.internal.adapters.output.postgres.role.repository import (
    PostgresRoleRepository,
)
from auth_api.internal.core.domain.models.role.role import ADMIN_ROLE_NAME
from auth_api.internal.ports.output.role_repository import RoleCreate
from auth_api.internal.pkg.errors import EntityNotFoundError, ForbiddenError


@pytest_asyncio.fixture
async def role_repo(db_session):
    """Role repository backed by a test database session."""
    return PostgresRoleRepository(db_session)


@pytest_asyncio.fixture(autouse=True)
async def _clean_roles(db_session):
    """Cleanup role-related tables before each test."""
    yield
    await db_session.execute(text("DELETE FROM service.user_roles"))
    await db_session.execute(text("DELETE FROM service.roles"))
    await db_session.commit()


class TestCreateRole:
    """Role creation tests."""

    @pytest.mark.asyncio
    async def test_create_role_returns_domain_role(self, role_repo):
        """create_role returns a domain Role instance."""
        role = await role_repo.create_role(RoleCreate(name="editor"))

        assert role.name == "editor"
        assert isinstance(role.id, uuid.UUID)

    @pytest.mark.asyncio
    async def test_create_admin_role(self, role_repo):
        """Creating admin role succeeds."""
        role = await role_repo.create_role(
            RoleCreate(name=ADMIN_ROLE_NAME))
        assert role.name == ADMIN_ROLE_NAME


class TestListRoles:
    """Role list tests."""

    @pytest.mark.asyncio
    async def test_list_roles_empty(self, role_repo):
        """Empty roles list is returned when table is empty."""
        roles = await role_repo.list_roles()
        assert roles == []

    @pytest.mark.asyncio
    async def test_list_roles_returns_all(self, role_repo):
        """list_roles returns all created roles."""
        await role_repo.create_role(RoleCreate(name="role1"))
        await role_repo.create_role(RoleCreate(name="role2"))

        roles = await role_repo.list_roles()
        names = {r.name for r in roles}
        assert names == {"role1", "role2"}


class TestGetRoleById:
    """Role retrieval by id tests."""

    @pytest.mark.asyncio
    async def test_get_existing_role(self, role_repo):
        """Existing role is returned by id."""
        created = await role_repo.create_role(RoleCreate(name="viewer"))
        found = await role_repo.get_role_by_id(created.id)

        assert found.id == created.id
        assert found.name == "viewer"

    @pytest.mark.asyncio
    async def test_get_nonexistent_role(self, role_repo):
        """EntityNotFoundError is raised for missing role."""
        with pytest.raises(EntityNotFoundError):
            await role_repo.get_role_by_id(uuid.uuid4())


class TestUpdateRole:
    """Role update tests."""

    @pytest.mark.asyncio
    async def test_update_role_name(self, role_repo):
        """Role name is updated correctly."""
        role = await role_repo.create_role(RoleCreate(name="oldname"))
        updated = await role_repo.update_role(role.id, "newname")

        assert updated.name == "newname"
        assert updated.id == role.id

    @pytest.mark.asyncio
    async def test_update_nonexistent_role(self, role_repo):
        """EntityNotFoundError is raised for missing role on update."""
        with pytest.raises(EntityNotFoundError):
            await role_repo.update_role(uuid.uuid4(), "newname")

    @pytest.mark.asyncio
    async def test_update_admin_role_raises_forbidden(self, role_repo):
        """Updating admin role raises ForbiddenError."""
        admin = await role_repo.create_role(
            RoleCreate(name=ADMIN_ROLE_NAME))
        with pytest.raises(ForbiddenError):
            await role_repo.update_role(admin.id, "renamed")


class TestDeleteRole:
    """Role delete tests."""

    @pytest.mark.asyncio
    async def test_delete_role_success(self, role_repo):
        """Role is removed from the database."""
        role = await role_repo.create_role(RoleCreate(name="todelete"))
        await role_repo.delete_role(role.id)

        with pytest.raises(EntityNotFoundError):
            await role_repo.get_role_by_id(role.id)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_role(self, role_repo):
        """Deleting missing role raises EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await role_repo.delete_role(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_delete_admin_role_raises_forbidden(self, role_repo):
        """Deleting admin role raises ForbiddenError."""
        admin = await role_repo.create_role(
            RoleCreate(name=ADMIN_ROLE_NAME))
        with pytest.raises(ForbiddenError):
            await role_repo.delete_role(admin.id)
