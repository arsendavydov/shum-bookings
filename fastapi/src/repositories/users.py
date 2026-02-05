from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.users_mapper import UsersMapper
from src.schemas.users import SchemaUser


class UsersRepository(BaseRepository[UsersOrm]):
    """
    Репозиторий для работы с пользователями.

    Наследует базовые CRUD методы и добавляет специфичные методы
    для работы с пользователями.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория пользователей.

        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        super().__init__(session, UsersOrm)

    def _to_schema(self, orm_obj: UsersOrm) -> SchemaUser:
        """
        Преобразовать ORM объект пользователя в Pydantic схему.

        Args:
            orm_obj: ORM объект пользователя

        Returns:
            Pydantic схема SchemaUser
        """
        return UsersMapper.to_schema(orm_obj)

    async def get_by_email(self, email: str) -> SchemaUser | None:
        """
        Получить пользователя по email (без пароля).

        Args:
            email: Email пользователя

        Returns:
            Pydantic схема SchemaUser или None, если не найдено
        """
        return await self.get_by_field("email", email)

    async def get_orm_by_email(self, email: str) -> UsersOrm | None:
        """
        Получить ORM объект пользователя по email (с паролем, для внутреннего использования).

        Args:
            email: Email пользователя

        Returns:
            ORM объект UsersOrm или None, если не найдено
        """
        return await self.get_by_field_orm("email", email)

    async def exists_by_email(self, email: str) -> bool:
        """
        Проверить существование пользователя с таким email.

        Args:
            email: Email пользователя

        Returns:
            True если пользователь существует, False иначе
        """
        return await self.exists_by_field("email", email)

    async def get_paginated(self, page: int, per_page: int, email: str | None = None) -> list[SchemaUser]:
        """
        Получить список пользователей с пагинацией и фильтрацией.

        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            email: Опциональный фильтр по email (точное совпадение)

        Returns:
            Список пользователей (Pydantic схемы SchemaUser)
        """
        query = select(self.model)

        # Применяем фильтр по email, если указан
        if email is not None:
            query = query.where(self.model.email == email)

        return await self._get_paginated_with_query(page, per_page, query)
