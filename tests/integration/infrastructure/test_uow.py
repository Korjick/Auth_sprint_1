import pytest
import pytest_asyncio
from sqlalchemy import text

from internal.infrastructure.uow import SqlAlchemyUnitOfWork
from internal.ports.output.user_repository import UserCreate
from internal.ports.output.role_repository import RoleCreate
from internal.pkg.errors import EntityNotFoundError


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(db_session):
    """Очистка таблиц после каждого теста."""
    yield
    await db_session.execute(text("DELETE FROM service.user_roles"))
    await db_session.execute(text("DELETE FROM service.sessions"))
    await db_session.execute(text("DELETE FROM service.users"))
    await db_session.execute(text("DELETE FROM service.roles"))
    await db_session.commit()


class TestUnitOfWork:
    """Тесты единицы работы (UoW) с реальной БД."""

    @pytest.mark.asyncio
    async def test_commit_persists_data(self, db_session_factory):
        """Данные сохраняются после commit."""
        uow = SqlAlchemyUnitOfWork(db_session_factory)

        async with uow:
            await uow.users.save_user(UserCreate(
                login="uow_user",
                password_hash="hash",
                first_name="UoW",
                last_name="Test",
                is_active=True,
            ))
            await uow.commit()

        # Проверяем в новой сессии
        async with uow:
            user = await uow.users.get_user_by_login("uow_user")
            assert user.login == "uow_user"

    @pytest.mark.asyncio
    async def test_rollback_discards_data(self, db_session_factory):
        """Данные не сохраняются после rollback."""
        uow = SqlAlchemyUnitOfWork(db_session_factory)

        async with uow:
            await uow.users.save_user(UserCreate(
                login="rollback_user",
                password_hash="hash",
                first_name="Rollback",
                last_name="Test",
                is_active=True,
            ))
            await uow.rollback()

        async with uow:
            with pytest.raises(EntityNotFoundError):
                await uow.users.get_user_by_login("rollback_user")

    @pytest.mark.asyncio
    async def test_exception_triggers_rollback(self, db_session_factory):
        """Исключение внутри контекстного менеджера откатывает транзакцию."""
        uow = SqlAlchemyUnitOfWork(db_session_factory)

        with pytest.raises(ValueError):
            async with uow:
                await uow.users.save_user(UserCreate(
                    login="exc_user",
                    password_hash="hash",
                    first_name="Exc",
                    last_name="Test",
                    is_active=True,
                ))
                raise ValueError("test error")

        async with uow:
            with pytest.raises(EntityNotFoundError):
                await uow.users.get_user_by_login("exc_user")

    @pytest.mark.asyncio
    async def test_uow_exposes_all_repositories(self, db_session_factory):
        """UoW предоставляет доступ к users, sessions и roles."""
        uow = SqlAlchemyUnitOfWork(db_session_factory)

        async with uow:
            assert uow.users is not None
            assert uow.sessions is not None
            assert uow.roles is not None

    @pytest.mark.asyncio
    async def test_create_role_through_uow(self, db_session_factory):
        """Роль создаётся и извлекается через UoW."""
        uow = SqlAlchemyUnitOfWork(db_session_factory)

        async with uow:
            role = await uow.roles.create_role(RoleCreate(name="testrole"))
            await uow.commit()

        async with uow:
            roles = await uow.roles.list_roles()
            assert any(r.name == "testrole" for r in roles)
