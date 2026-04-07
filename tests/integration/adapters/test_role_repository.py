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
    """Р РµРїРѕР·РёС‚РѕСЂРёР№ СЂРѕР»РµР№ СЃ С‚РµСЃС‚РѕРІРѕР№ СЃРµСЃСЃРёРµР№."""
    return PostgresRoleRepository(db_session)


@pytest_asyncio.fixture(autouse=True)
async def _clean_roles(db_session):
    """РћС‡РёСЃС‚РєР° С‚Р°Р±Р»РёС† СЂРѕР»РµР№ РїРµСЂРµРґ РєР°Р¶РґС‹Рј С‚РµСЃС‚РѕРј."""
    yield
    await db_session.execute(text("DELETE FROM service.user_roles"))
    await db_session.execute(text("DELETE FROM service.roles"))
    await db_session.commit()


class TestCreateRole:
    """РўРµСЃС‚С‹ СЃРѕР·РґР°РЅРёСЏ СЂРѕР»Рё."""

    @pytest.mark.asyncio
    async def test_create_role_returns_domain_role(self, role_repo):
        """create_role РІРѕР·РІСЂР°С‰Р°РµС‚ РґРѕРјРµРЅРЅСѓСЋ РјРѕРґРµР»СЊ Role."""
        role = await role_repo.create_role(RoleCreate(name="editor"))

        assert role.name == "editor"
        assert isinstance(role.id, uuid.UUID)

    @pytest.mark.asyncio
    async def test_create_admin_role(self, role_repo):
        """РЎРѕР·РґР°РЅРёРµ СЂРѕР»Рё admin РїСЂРѕС…РѕРґРёС‚ СѓСЃРїРµС€РЅРѕ."""
        role = await role_repo.create_role(
            RoleCreate(name=ADMIN_ROLE_NAME))
        assert role.name == ADMIN_ROLE_NAME


class TestListRoles:
    """РўРµСЃС‚С‹ РїРѕР»СѓС‡РµРЅРёСЏ СЃРїРёСЃРєР° СЂРѕР»РµР№."""

    @pytest.mark.asyncio
    async def test_list_roles_empty(self, role_repo):
        """РџСѓСЃС‚РѕР№ СЃРїРёСЃРѕРє СЂРѕР»РµР№."""
        roles = await role_repo.list_roles()
        assert roles == []

    @pytest.mark.asyncio
    async def test_list_roles_returns_all(self, role_repo):
        """list_roles РІРѕР·РІСЂР°С‰Р°РµС‚ РІСЃРµ СЃРѕР·РґР°РЅРЅС‹Рµ СЂРѕР»Рё."""
        await role_repo.create_role(RoleCreate(name="role1"))
        await role_repo.create_role(RoleCreate(name="role2"))

        roles = await role_repo.list_roles()
        names = {r.name for r in roles}
        assert names == {"role1", "role2"}


class TestGetRoleById:
    """РўРµСЃС‚С‹ РїРѕР»СѓС‡РµРЅРёСЏ СЂРѕР»Рё РїРѕ id."""

    @pytest.mark.asyncio
    async def test_get_existing_role(self, role_repo):
        """РЎСѓС‰РµСЃС‚РІСѓСЋС‰Р°СЏ СЂРѕР»СЊ РІРѕР·РІСЂР°С‰Р°РµС‚СЃСЏ РїРѕ id."""
        created = await role_repo.create_role(RoleCreate(name="viewer"))
        found = await role_repo.get_role_by_id(created.id)

        assert found.id == created.id
        assert found.name == "viewer"

    @pytest.mark.asyncio
    async def test_get_nonexistent_role(self, role_repo):
        """РќРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰Р°СЏ СЂРѕР»СЊ РІС‹Р·С‹РІР°РµС‚ EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await role_repo.get_role_by_id(uuid.uuid4())


class TestUpdateRole:
    """РўРµСЃС‚С‹ РѕР±РЅРѕРІР»РµРЅРёСЏ СЂРѕР»Рё."""

    @pytest.mark.asyncio
    async def test_update_role_name(self, role_repo):
        """РРјСЏ СЂРѕР»Рё РѕР±РЅРѕРІР»СЏРµС‚СЃСЏ РєРѕСЂСЂРµРєС‚РЅРѕ."""
        role = await role_repo.create_role(RoleCreate(name="oldname"))
        updated = await role_repo.update_role(role.id, "newname")

        assert updated.name == "newname"
        assert updated.id == role.id

    @pytest.mark.asyncio
    async def test_update_nonexistent_role(self, role_repo):
        """РћР±РЅРѕРІР»РµРЅРёРµ РЅРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РµР№ СЂРѕР»Рё РІС‹Р·С‹РІР°РµС‚ EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await role_repo.update_role(uuid.uuid4(), "newname")

    @pytest.mark.asyncio
    async def test_update_admin_role_raises_forbidden(self, role_repo):
        """РћР±РЅРѕРІР»РµРЅРёРµ admin-СЂРѕР»Рё РІС‹Р·С‹РІР°РµС‚ ForbiddenError."""
        admin = await role_repo.create_role(
            RoleCreate(name=ADMIN_ROLE_NAME))
        with pytest.raises(ForbiddenError):
            await role_repo.update_role(admin.id, "renamed")


class TestDeleteRole:
    """РўРµСЃС‚С‹ СѓРґР°Р»РµРЅРёСЏ СЂРѕР»Рё."""

    @pytest.mark.asyncio
    async def test_delete_role_success(self, role_repo):
        """Р РѕР»СЊ СѓРґР°Р»СЏРµС‚СЃСЏ РёР· Р‘Р”."""
        role = await role_repo.create_role(RoleCreate(name="todelete"))
        await role_repo.delete_role(role.id)

        with pytest.raises(EntityNotFoundError):
            await role_repo.get_role_by_id(role.id)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_role(self, role_repo):
        """РЈРґР°Р»РµРЅРёРµ РЅРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РµР№ СЂРѕР»Рё РІС‹Р·С‹РІР°РµС‚ EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await role_repo.delete_role(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_delete_admin_role_raises_forbidden(self, role_repo):
        """РЈРґР°Р»РµРЅРёРµ admin-СЂРѕР»Рё РІС‹Р·С‹РІР°РµС‚ ForbiddenError."""
        admin = await role_repo.create_role(
            RoleCreate(name=ADMIN_ROLE_NAME))
        with pytest.raises(ForbiddenError):
            await role_repo.delete_role(admin.id)

