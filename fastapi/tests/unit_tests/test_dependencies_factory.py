"""
Unit тесты для generic фабрики репозиториев в dependencies.py.

Проверяют, что фабрика create_repository_dependency работает корректно.
"""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api.dependencies import create_repository_dependency
from src.utils.db_manager import DBManager

pytestmark = pytest.mark.unit


class MockRepository:
    """Мок-репозиторий для тестирования."""

    def __init__(self, session):
        self.session = session


@pytest.fixture
def mock_db():
    """Фикстура для создания мока сессии БД."""
    return AsyncMock()


@pytest.fixture
def mock_get_repo_method():
    """Фикстура для создания мока метода получения репозитория."""
    return MagicMock(return_value=MockRepository(AsyncMock()))


class TestCreateRepositoryDependency:
    """Тесты для фабрики create_repository_dependency."""

    @pytest.mark.asyncio
    async def test_create_read_repository_dependency(self, mock_db, mock_get_repo_method):
        """Проверить, что фабрика создает функцию для чтения репозитория."""
        get_repo, _ = create_repository_dependency(mock_get_repo_method, MockRepository)

        # Мокируем get_db
        with patch("src.api.dependencies.get_db") as mock_get_db:
            mock_get_db.return_value = AsyncMock()
            mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_get_db.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await get_repo(mock_db)

        assert isinstance(result, MockRepository)
        mock_get_repo_method.assert_called_once_with(mock_db)

    @pytest.mark.asyncio
    async def test_create_write_repository_dependency_success(self, mock_db, mock_get_repo_method):
        """Проверить, что фабрика создает функцию для записи с commit при успехе."""
        _, get_repo_with_commit = create_repository_dependency(mock_get_repo_method, MockRepository)

        # Мокируем DBManager.commit
        with patch("src.api.dependencies.DBManager.commit", new_callable=AsyncMock) as mock_commit:
            async_gen = get_repo_with_commit(mock_db)
            repo = await async_gen.__anext__()

            assert isinstance(repo, MockRepository)
            mock_get_repo_method.assert_called_once_with(mock_db)

            # Завершаем генератор (успешный сценарий)
            try:
                await async_gen.__anext__()
            except StopAsyncIteration:
                pass

            mock_commit.assert_called_once_with(mock_db)

    @pytest.mark.asyncio
    async def test_create_write_repository_dependency_is_generator(self, mock_db, mock_get_repo_method):
        """Проверить, что фабрика создает async генератор для записи."""
        _, get_repo_with_commit = create_repository_dependency(mock_get_repo_method, MockRepository)

        # Проверяем, что функция возвращает async генератор
        async_gen = get_repo_with_commit(mock_db)
        assert hasattr(async_gen, "__anext__")
        assert hasattr(async_gen, "__aiter__")

    def test_factory_returns_two_functions(self, mock_get_repo_method):
        """Проверить, что фабрика возвращает две функции."""
        get_repo, get_repo_with_commit = create_repository_dependency(
            mock_get_repo_method, MockRepository
        )

        assert callable(get_repo)
        assert callable(get_repo_with_commit)

