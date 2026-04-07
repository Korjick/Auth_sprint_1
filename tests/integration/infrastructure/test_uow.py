import pytest
import pytest_asyncio
from sqlalchemy import text

from auth_api.internal.infrastructure.uow import SqlAlchemyUnitOfWork
from auth_api.internal.ports.output.user_repository import UserCreate
from auth_api.internal.ports.output.role_repository import RoleCreate
from auth_api.internal.pkg.errors import EntityNotFoundError


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(db_session):
    """Cleanup tables after each test."""
    yield
    await db_session.execute(text("DELETE FROM service.user_roles"))
    await db_session.execute(text("DELETE FROM service.sessions"))
    await db_session.execute(text("DELETE FROM service.users"))
    await db_session.execute(text("DELETE FROM service.roles"))
    await db_session.commit()


class TestUnitOfWork:
    """Unit of Work integration tests with a real database."""

    @pytest.mark.asyncio
    async def test_commit_persists_data(self, db_session_factory):
        """Data is persisted after commit."""
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

        async with uow:
            user = await uow.users.get_user_by_login("uow_user")
            assert user.login == "uow_user"

    @pytest.mark.asyncio
    async def test_rollback_discards_data(self, db_session_factory):
        """Data is not persisted after rollback."""
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
        """Exception inside context manager triggers rollback."""
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
        """UoW exposes users, sessions and roles repositories."""
        uow = SqlAlchemyUnitOfWork(db_session_factory)

        async with uow:
            assert uow.users is not None
            assert uow.sessions is not None
            assert uow.roles is not None

    @pytest.mark.asyncio
    async def test_create_role_through_uow(self, db_session_factory):
        """Role can be created and fetched through UoW."""
        uow = SqlAlchemyUnitOfWork(db_session_factory)

        async with uow:
            await uow.roles.create_role(RoleCreate(name="testrole"))
            await uow.commit()

        async with uow:
            roles = await uow.roles.list_roles()
            assert any(r.name == "testrole" for r in roles)
