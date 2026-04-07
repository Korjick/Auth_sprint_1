import uuid
import datetime

import pytest
import pytest_asyncio
from sqlalchemy import text

from auth_api.internal.adapters.output.postgres.session.repository import (
    PostgresSessionRepository,
)
from auth_api.internal.adapters.output.postgres.user.repository import (
    PostgresUserRepository,
)
from auth_api.internal.ports.output.session_repository import SessionCreate
from auth_api.internal.ports.output.user_repository import UserCreate
from auth_api.internal.core.domain.models.session.session import Session
from auth_api.internal.pkg.errors import EntityNotFoundError


@pytest_asyncio.fixture
async def user_repo(db_session):
    return PostgresUserRepository(db_session)


@pytest_asyncio.fixture
async def session_repo(db_session):
    return PostgresSessionRepository(db_session)


@pytest_asyncio.fixture
async def test_user(user_repo):
    """Создаёт тестового пользователя и возвращает доменную модель."""
    return await user_repo.save_user(UserCreate(
        login=f"session_user_{uuid.uuid4().hex[:8]}",
        password_hash="hashed",
        first_name="Session",
        last_name="Tester",
        is_active=True,
    ))


@pytest_asyncio.fixture(autouse=True)
async def _clean_sessions(db_session):
    """Очистка таблиц после каждого теста."""
    yield
    await db_session.execute(text("DELETE FROM service.sessions"))
    await db_session.execute(text("DELETE FROM service.user_roles"))
    await db_session.execute(text("DELETE FROM service.users"))
    await db_session.commit()


def _session_create(user_id: uuid.UUID, **overrides) -> SessionCreate:
    defaults = dict(
        user_id=user_id,
        jti=uuid.uuid4(),
        device_fingerprint="Chrome|en|127.0.0.1",
        expires_at=datetime.datetime(2025, 12, 31, 23, 59, 59),
    )
    defaults.update(overrides)
    return SessionCreate(**defaults)


class TestCreateSession:
    """Тесты создания сессии."""

    @pytest.mark.asyncio
    async def test_create_session_returns_domain_session(
            self, session_repo, test_user):
        """create_session возвращает доменную модель Session."""
        sc = _session_create(test_user.id)
        session = await session_repo.create_session(sc)

        assert isinstance(session.id, uuid.UUID)
        assert session.user_id == test_user.id
        assert session.jti == sc.jti
        assert session.device_fingerprint == sc.device_fingerprint


class TestGetSessionByJti:
    """Тесты поиска сессии по JTI."""

    @pytest.mark.asyncio
    async def test_get_existing_session(self, session_repo, test_user):
        """Существующая сессия находится по jti."""
        sc = _session_create(test_user.id)
        created = await session_repo.create_session(sc)

        found = await session_repo.get_session_by_jti(created.jti)
        assert found.id == created.id
        assert found.jti == created.jti

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, session_repo):
        """Несуществующая сессия вызывает EntityNotFoundError."""
        with pytest.raises(EntityNotFoundError):
            await session_repo.get_session_by_jti(uuid.uuid4())


class TestUpdateSession:
    """Тесты обновления сессии."""

    @pytest.mark.asyncio
    async def test_update_session_jti_and_expiry(
            self, session_repo, test_user):
        """Обновление jti и expire_at сессии."""
        sc = _session_create(test_user.id)
        created = await session_repo.create_session(sc)

        new_jti = uuid.uuid4()
        new_expire = datetime.datetime(2026, 6, 15, 12, 0, 0)

        updated_session = Session(
            oid=created.id,
            user_id=created.user_id,
            jti=new_jti,
            device_fingerprint=created.device_fingerprint,
            expire_at=new_expire,
        )
        result = await session_repo.update_session(updated_session)

        assert result.jti == new_jti
        assert result.expire_at == new_expire

    @pytest.mark.asyncio
    async def test_update_nonexistent_session(self, session_repo, test_user):
        """Обновление несуществующей сессии вызывает ошибку."""
        fake_session = Session(
            oid=uuid.uuid4(),
            user_id=test_user.id,
            jti=uuid.uuid4(),
            device_fingerprint="x",
            expire_at=datetime.datetime(2025, 1, 1),
        )
        with pytest.raises(EntityNotFoundError):
            await session_repo.update_session(fake_session)


class TestDeleteSession:
    """Тесты удаления сессий."""

    @pytest.mark.asyncio
    async def test_delete_session_by_jti(self, session_repo, test_user):
        """Сессия удаляется по jti."""
        sc = _session_create(test_user.id)
        created = await session_repo.create_session(sc)

        await session_repo.delete_session(created.jti)

        with pytest.raises(EntityNotFoundError):
            await session_repo.get_session_by_jti(created.jti)

    @pytest.mark.asyncio
    async def test_delete_by_user_id(self, session_repo, test_user):
        """Все сессии пользователя удаляются."""
        await session_repo.create_session(
            _session_create(test_user.id, jti=uuid.uuid4()))
        await session_repo.create_session(
            _session_create(test_user.id, jti=uuid.uuid4()))

        await session_repo.delete_by_user_id(test_user.id)

        sessions = await session_repo.get_sessions_by_user_id(test_user.id)
        assert len(sessions) == 0

    @pytest.mark.asyncio
    async def test_delete_by_user_id_and_fingerprint(
            self, session_repo, test_user):
        """Удаление сессий конкретного устройства."""
        fp1 = "Chrome|en|127.0.0.1"
        fp2 = "Firefox|ru|10.0.0.1"
        await session_repo.create_session(
            _session_create(test_user.id,
                            device_fingerprint=fp1, jti=uuid.uuid4()))
        await session_repo.create_session(
            _session_create(test_user.id,
                            device_fingerprint=fp2, jti=uuid.uuid4()))

        await session_repo.delete_by_user_id_and_fingerprint(
            test_user.id, fp1)

        sessions = await session_repo.get_sessions_by_user_id(test_user.id)
        assert len(sessions) == 1
        assert sessions[0].device_fingerprint == fp2


class TestGetSessionsByUserId:
    """Тесты получения списка сессий пользователя."""

    @pytest.mark.asyncio
    async def test_get_sessions_empty(self, session_repo, test_user):
        """Пустой список сессий для нового пользователя."""
        sessions = await session_repo.get_sessions_by_user_id(test_user.id)
        assert sessions == []

    @pytest.mark.asyncio
    async def test_get_sessions_returns_all(self, session_repo, test_user):
        """Возвращаются все сессии пользователя."""
        await session_repo.create_session(
            _session_create(test_user.id, jti=uuid.uuid4()))
        await session_repo.create_session(
            _session_create(test_user.id, jti=uuid.uuid4()))

        sessions = await session_repo.get_sessions_by_user_id(test_user.id)
        assert len(sessions) == 2

