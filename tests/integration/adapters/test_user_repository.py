import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text

from auth_api.internal.adapters.output.postgres.user.repository import (
    PostgresUserRepository,
)
from auth_api.internal.adapters.output.postgres.role.repository import (
    PostgresRoleRepository,
)
from auth_api.internal.ports.output.user_repository import UserCreate
from auth_api.internal.ports.output.role_repository import RoleCreate
from auth_api.internal.pkg.errors import EntityNotFoundError


@pytest_asyncio.fixture
async def user_repo(db_session):
    """Р РµРїРѕР·РёС‚РѕСЂРёР№ РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№ СЃ С‚РµСЃС‚РѕРІРѕР№ СЃРµСЃСЃРёРµР№."""
    return PostgresUserRepository(db_session)


@pytest_asyncio.fixture
async def role_repo(db_session):
    """Р РµРїРѕР·РёС‚РѕСЂРёР№ СЂРѕР»РµР№ СЃ С‚РµСЃС‚РѕРІРѕР№ СЃРµСЃСЃРёРµР№."""
    return PostgresRoleRepository(db_session)


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(db_session):
    """РћС‡РёСЃС‚РєР° С‚Р°Р±Р»РёС† РїРµСЂРµРґ РєР°Р¶РґС‹Рј С‚РµСЃС‚РѕРј."""
    yield
    await db_session.execute(text("DELETE FROM service.user_roles"))
    await db_session.execute(text("DELETE FROM service.sessions"))
    await db_session.execute(text("DELETE FROM service.users"))
    await db_session.execute(text("DELETE FROM service.roles"))
    await db_session.commit()


def _user_create(**overrides) -> UserCreate:
    defaults = dict(
        login="testuser",
        password_hash="hashed_pwd_123",
        first_name="Test",
        last_name="User",
        is_superuser=False,
        is_active=True,
    )
    defaults.update(overrides)
    return UserCreate(**defaults)


class TestSaveUser:
    """РўРµСЃС‚С‹ СЃРѕР·РґР°РЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РІ Р‘Р”."""

    @pytest.mark.asyncio
    async def test_save_user_returns_domain_user(self, user_repo):
        """save_user РІРѕР·РІСЂР°С‰Р°РµС‚ РґРѕРјРµРЅРЅСѓСЋ РјРѕРґРµР»СЊ User."""
        user = await user_repo.save_user(_user_create())

        assert user.login == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert isinstance(user.id, uuid.UUID)
        assert user.roles == []

    @pytest.mark.asyncio
    async def test_save_superuser(self, user_repo):
        """РЎСѓРїРµСЂРїРѕР»СЊР·РѕРІР°С‚РµР»СЊ СЃРѕС…СЂР°РЅСЏРµС‚СЃСЏ СЃ С„Р»Р°РіРѕРј is_superuser=True."""
        user = await user_repo.save_user(
            _user_create(login="super", is_superuser=True)
        )
        assert user.is_superuser is True


class TestGetUserByLogin:
    """РўРµСЃС‚С‹ РїРѕР»СѓС‡РµРЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РїРѕ Р»РѕРіРёРЅСѓ."""

    @pytest.mark.asyncio
    async def test_get_existing_user(self, user_repo):
        """РЎСѓС‰РµСЃС‚РІСѓСЋС‰РёР№ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ РІРѕР·РІСЂР°С‰Р°РµС‚СЃСЏ РїРѕ Р»РѕРіРёРЅСѓ."""
        await user_repo.save_user(_user_create(login="alice"))
        user = await user_repo.get_user_by_login("alice")

        assert user.login == "alice"

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_raises(self, user_repo):
        """РќРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РёР№ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ РІС‹Р·С‹РІР°РµС‚ EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await user_repo.get_user_by_login("nonexistent")


class TestGetUserById:
    """РўРµСЃС‚С‹ РїРѕР»СѓС‡РµРЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РїРѕ UUID."""

    @pytest.mark.asyncio
    async def test_get_existing_user(self, user_repo):
        """РЎСѓС‰РµСЃС‚РІСѓСЋС‰РёР№ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ РІРѕР·РІСЂР°С‰Р°РµС‚СЃСЏ РїРѕ UUID."""
        created = await user_repo.save_user(_user_create(login="alice"))
        user = await user_repo.get_user_by_id(created.id)

        assert user.id == created.id
        assert user.login == "alice"

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_raises(self, user_repo):
        """РќРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РёР№ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ РїРѕ UUID РІС‹Р·С‹РІР°РµС‚ EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await user_repo.get_user_by_id(uuid.uuid4())


class TestUpdateLogin:
    """РўРµСЃС‚С‹ РѕР±РЅРѕРІР»РµРЅРёСЏ Р»РѕРіРёРЅР°."""

    @pytest.mark.asyncio
    async def test_update_login_success(self, user_repo):
        """Р›РѕРіРёРЅ РѕР±РЅРѕРІР»СЏРµС‚СЃСЏ Рё РІРѕР·РІСЂР°С‰Р°РµС‚СЃСЏ РѕР±РЅРѕРІР»С‘РЅРЅС‹Р№ User."""
        user = await user_repo.save_user(_user_create(login="old_login"))
        updated = await user_repo.update_login(user.id, "new_login")

        assert updated.login == "new_login"
        assert updated.id == user.id

    @pytest.mark.asyncio
    async def test_update_login_nonexistent_user(self, user_repo):
        """РћР±РЅРѕРІР»РµРЅРёРµ Р»РѕРіРёРЅР° РЅРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РµРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РІС‹Р·С‹РІР°РµС‚ РѕС€РёР±РєСѓ."""
        with pytest.raises(EntityNotFoundError):
            await user_repo.update_login(uuid.uuid4(), "new_login")


class TestUpdatePassword:
    """РўРµСЃС‚С‹ РѕР±РЅРѕРІР»РµРЅРёСЏ РїР°СЂРѕР»СЏ."""

    @pytest.mark.asyncio
    async def test_update_password_success(self, user_repo):
        """РџР°СЂРѕР»СЊ РѕР±РЅРѕРІР»СЏРµС‚СЃСЏ Рё РІРѕР·РІСЂР°С‰Р°РµС‚СЃСЏ РѕР±РЅРѕРІР»С‘РЅРЅС‹Р№ User."""
        user = await user_repo.save_user(_user_create())
        updated = await user_repo.update_password(user.id, "new_hash")

        assert updated.password_hash == "new_hash"

    @pytest.mark.asyncio
    async def test_update_password_nonexistent_user(self, user_repo):
        """РћР±РЅРѕРІР»РµРЅРёРµ РїР°СЂРѕР»СЏ РЅРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РµРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РІС‹Р·С‹РІР°РµС‚ РѕС€РёР±РєСѓ."""
        with pytest.raises(EntityNotFoundError):
            await user_repo.update_password(uuid.uuid4(), "new_hash")


class TestUserRoles:
    """РўРµСЃС‚С‹ РЅР°Р·РЅР°С‡РµРЅРёСЏ Рё СѓРґР°Р»РµРЅРёСЏ СЂРѕР»РµР№ Сѓ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""

    @pytest.mark.asyncio
    async def test_add_role_to_user(self, user_repo, role_repo):
        """Р РѕР»СЊ РґРѕР±Р°РІР»СЏРµС‚СЃСЏ Рє РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ."""
        user = await user_repo.save_user(_user_create(login="role_user"))
        role = await role_repo.create_role(RoleCreate(name="editor"))

        updated = await user_repo.add_role(user.id, role.id)
        assert "editor" in updated.roles

    @pytest.mark.asyncio
    async def test_add_same_role_twice_is_idempotent(
            self, user_repo, role_repo):
        """РџРѕРІС‚РѕСЂРЅРѕРµ РґРѕР±Р°РІР»РµРЅРёРµ С‚РѕР№ Р¶Рµ СЂРѕР»Рё РЅРµ СЃРѕР·РґР°С‘С‚ РґСѓР±Р»РёРєР°С‚."""
        user = await user_repo.save_user(
            _user_create(login="idem_user"))
        role = await role_repo.create_role(RoleCreate(name="viewer"))

        await user_repo.add_role(user.id, role.id)
        updated = await user_repo.add_role(user.id, role.id)
        assert updated.roles.count("viewer") == 1

    @pytest.mark.asyncio
    async def test_remove_role_from_user(self, user_repo, role_repo):
        """Р РѕР»СЊ СѓРґР°Р»СЏРµС‚СЃСЏ Сѓ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
        user = await user_repo.save_user(
            _user_create(login="rm_role_user"))
        role = await role_repo.create_role(RoleCreate(name="temp"))

        await user_repo.add_role(user.id, role.id)
        updated = await user_repo.remove_role(user.id, role.id)
        assert "temp" not in updated.roles

    @pytest.mark.asyncio
    async def test_add_role_nonexistent_user(self, user_repo, role_repo):
        """Р”РѕР±Р°РІР»РµРЅРёРµ СЂРѕР»Рё РЅРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РµРјСѓ РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ РІС‹Р·С‹РІР°РµС‚ РѕС€РёР±РєСѓ."""
        role = await role_repo.create_role(RoleCreate(name="nouser"))
        with pytest.raises(EntityNotFoundError):
            await user_repo.add_role(uuid.uuid4(), role.id)

    @pytest.mark.asyncio
    async def test_add_nonexistent_role(self, user_repo):
        """Р”РѕР±Р°РІР»РµРЅРёРµ РЅРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РµР№ СЂРѕР»Рё РІС‹Р·С‹РІР°РµС‚ РѕС€РёР±РєСѓ."""
        user = await user_repo.save_user(
            _user_create(login="norole_user"))
        with pytest.raises(EntityNotFoundError):
            await user_repo.add_role(user.id, uuid.uuid4())

