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
    """Репозиторий пользователей с тестовой сессией."""
    return PostgresUserRepository(db_session)


@pytest_asyncio.fixture
async def role_repo(db_session):
    """Репозиторий ролей с тестовой сессией."""
    return PostgresRoleRepository(db_session)


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(db_session):
    """Очистка таблиц перед каждым тестом."""
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
    """Тесты создания пользователя в БД."""

    @pytest.mark.asyncio
    async def test_save_user_returns_domain_user(self, user_repo):
        """save_user возвращает доменную модель User."""
        user = await user_repo.save_user(_user_create())

        assert user.login == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert isinstance(user.id, uuid.UUID)
        assert user.roles == []

    @pytest.mark.asyncio
    async def test_save_superuser(self, user_repo):
        """Суперпользователь сохраняется с флагом is_superuser=True."""
        user = await user_repo.save_user(
            _user_create(login="super", is_superuser=True)
        )
        assert user.is_superuser is True


class TestGetUserByLogin:
    """Тесты получения пользователя по логину."""

    @pytest.mark.asyncio
    async def test_get_existing_user(self, user_repo):
        """Существующий пользователь возвращается по логину."""
        await user_repo.save_user(_user_create(login="alice"))
        user = await user_repo.get_user_by_login("alice")

        assert user.login == "alice"

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_raises(self, user_repo):
        """Несуществующий пользователь вызывает EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await user_repo.get_user_by_login("nonexistent")


class TestGetUserById:
    """Тесты получения пользователя по UUID."""

    @pytest.mark.asyncio
    async def test_get_existing_user(self, user_repo):
        """Существующий пользователь возвращается по UUID."""
        created = await user_repo.save_user(_user_create(login="alice"))
        user = await user_repo.get_user_by_id(created.id)

        assert user.id == created.id
        assert user.login == "alice"

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_raises(self, user_repo):
        """Несуществующий пользователь по UUID вызывает EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await user_repo.get_user_by_id(uuid.uuid4())


class TestUpdateLogin:
    """Тесты обновления логина."""

    @pytest.mark.asyncio
    async def test_update_login_success(self, user_repo):
        """Логин обновляется и возвращается обновлённый User."""
        user = await user_repo.save_user(_user_create(login="old_login"))
        updated = await user_repo.update_login(user.id, "new_login")

        assert updated.login == "new_login"
        assert updated.id == user.id

    @pytest.mark.asyncio
    async def test_update_login_nonexistent_user(self, user_repo):
        """Обновление логина несуществующего пользователя вызывает ошибку."""
        with pytest.raises(EntityNotFoundError):
            await user_repo.update_login(uuid.uuid4(), "new_login")


class TestUpdatePassword:
    """Тесты обновления пароля."""

    @pytest.mark.asyncio
    async def test_update_password_success(self, user_repo):
        """Пароль обновляется и возвращается обновлённый User."""
        user = await user_repo.save_user(_user_create())
        updated = await user_repo.update_password(user.id, "new_hash")

        assert updated.password_hash == "new_hash"

    @pytest.mark.asyncio
    async def test_update_password_nonexistent_user(self, user_repo):
        """Обновление пароля несуществующего пользователя вызывает ошибку."""
        with pytest.raises(EntityNotFoundError):
            await user_repo.update_password(uuid.uuid4(), "new_hash")


class TestUserRoles:
    """Тесты назначения и удаления ролей у пользователя."""

    @pytest.mark.asyncio
    async def test_add_role_to_user(self, user_repo, role_repo):
        """Роль добавляется к пользователю."""
        user = await user_repo.save_user(_user_create(login="role_user"))
        role = await role_repo.create_role(RoleCreate(name="editor"))

        updated = await user_repo.add_role(user.id, role.id)
        assert "editor" in updated.roles

    @pytest.mark.asyncio
    async def test_add_same_role_twice_is_idempotent(
            self, user_repo, role_repo):
        """Повторное добавление той же роли не создаёт дубликат."""
        user = await user_repo.save_user(
            _user_create(login="idem_user"))
        role = await role_repo.create_role(RoleCreate(name="viewer"))

        await user_repo.add_role(user.id, role.id)
        updated = await user_repo.add_role(user.id, role.id)
        assert updated.roles.count("viewer") == 1

    @pytest.mark.asyncio
    async def test_remove_role_from_user(self, user_repo, role_repo):
        """Роль удаляется у пользователя."""
        user = await user_repo.save_user(
            _user_create(login="rm_role_user"))
        role = await role_repo.create_role(RoleCreate(name="temp"))

        await user_repo.add_role(user.id, role.id)
        updated = await user_repo.remove_role(user.id, role.id)
        assert "temp" not in updated.roles

    @pytest.mark.asyncio
    async def test_add_role_nonexistent_user(self, user_repo, role_repo):
        """Добавление роли несуществующему пользователю вызывает ошибку."""
        role = await role_repo.create_role(RoleCreate(name="nouser"))
        with pytest.raises(EntityNotFoundError):
            await user_repo.add_role(uuid.uuid4(), role.id)

    @pytest.mark.asyncio
    async def test_add_nonexistent_role(self, user_repo):
        """Добавление несуществующей роли вызывает ошибку."""
        user = await user_repo.save_user(
            _user_create(login="norole_user"))
        with pytest.raises(EntityNotFoundError):
            await user_repo.add_role(user.id, uuid.uuid4())

