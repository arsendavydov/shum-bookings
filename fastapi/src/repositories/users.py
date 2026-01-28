from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.repositories.base import BaseRepository
from src.repositories.utils import apply_pagination
from src.models.users import UsersOrm
from src.schemas.users import User
from src.repositories.mappers.users_mapper import UsersMapper


class UsersRepository(BaseRepository[UsersOrm]):
    """
    Репозиторий для работы с пользователями.
    
    Наследует базовые CRUD методы и добавляет специфичные методы
    для работы с пользователями.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория пользователей.
        
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        super().__init__(session, UsersOrm)
    
    def _to_schema(self, orm_obj: UsersOrm) -> User:
        """
        Преобразовать ORM объект пользователя в Pydantic схему.
        
        Args:
            orm_obj: ORM объект пользователя
            
        Returns:
            Pydantic схема User
        """
        return UsersMapper.to_schema(orm_obj)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email.
        
        Args:
            email: Email пользователя
            
        Returns:
            Pydantic схема User или None, если не найдено
        """
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        orm_obj = result.scalar_one_or_none()
        
        if orm_obj is None:
            return None
        
        return self._to_schema(orm_obj)
    
    async def exists_by_email(self, email: str) -> bool:
        """
        Проверить существование пользователя с таким email.
        
        Args:
            email: Email пользователя
            
        Returns:
            True если пользователь существует, False иначе
        """
        query = select(func.count(self.model.id)).where(self.model.email == email)
        result = await self.session.execute(query)
        count = result.scalar_one() or 0
        return count > 0
    
    async def get_paginated(
        self,
        page: int,
        per_page: int,
        email: Optional[str] = None
    ) -> List[User]:
        """
        Получить список пользователей с пагинацией и фильтрацией.
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            email: Опциональный фильтр по email (точное совпадение)
            
        Returns:
            Список пользователей (Pydantic схемы)
        """
        query = select(self.model)
        
        # Применяем фильтр по email, если указан
        if email is not None:
            query = query.where(self.model.email == email)
        
        # Применяем пагинацию
        query = apply_pagination(query, page, per_page)
        
        result = await self.session.execute(query)
        orm_objs = list(result.scalars().all())
        
        return [self._to_schema(obj) for obj in orm_objs]

