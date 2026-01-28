from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.repositories.base import BaseRepository
from src.repositories.utils import apply_pagination, apply_text_filter
from src.models.cities import CitiesOrm
from src.schemas.cities import SchemaCity
from src.repositories.mappers.cities_mapper import CitiesMapper


class CitiesRepository(BaseRepository[CitiesOrm]):
    """
    Репозиторий для работы с городами.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория городов.
        
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        super().__init__(session, CitiesOrm)
    
    def _to_schema(self, orm_obj: CitiesOrm) -> SchemaCity:
        """
        Преобразовать ORM объект города в Pydantic схему.
        
        Args:
            orm_obj: ORM объект города
            
        Returns:
            Pydantic схема SchemaCity
        """
        return CitiesMapper.to_schema(orm_obj)
    
    async def get_paginated(
        self,
        page: int,
        per_page: int,
        name: Optional[str] = None,
        country_id: Optional[int] = None
    ) -> List[SchemaCity]:
        """
        Получить список городов с пагинацией и фильтрацией.
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            name: Опциональный фильтр по названию (частичное совпадение, без учета регистра)
            country_id: Опциональный фильтр по ID страны (точное совпадение)
            
        Returns:
            Список городов (Pydantic схемы)
        """
        from sqlalchemy.orm import selectinload
        
        query = select(self.model).options(
            selectinload(self.model.country)
        )
        
        # Применяем фильтр по name, если указан
        if name is not None:
            query = apply_text_filter(query, self.model.name, name)
        
        # Применяем фильтр по country_id, если указан
        if country_id is not None:
            query = query.where(self.model.country_id == country_id)
        
        # Применяем пагинацию
        query = apply_pagination(query, page, per_page)
        
        result = await self.session.execute(query)
        orm_objs = list(result.scalars().all())
        
        return [self._to_schema(obj) for obj in orm_objs]
    
    async def get_by_id(self, id: int) -> Optional[SchemaCity]:
        """
        Получить город по ID с загрузкой связанной страны.
        
        Args:
            id: ID города
            
        Returns:
            Pydantic схема города или None, если не найдено
        """
        from sqlalchemy.orm import selectinload
        
        query = select(self.model).options(
            selectinload(self.model.country)
        ).where(self.model.id == id)
        result = await self.session.execute(query)
        orm_obj = result.scalar_one_or_none()
        
        if orm_obj is None:
            return None
        
        return self._to_schema(orm_obj)
    
    async def get_by_id_orm(self, id: int) -> Optional[CitiesOrm]:
        """
        Получить город по ID как ORM объект (для валидации).
        
        Args:
            id: ID города
            
        Returns:
            ORM объект города или None, если не найдено
        """
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name_and_country_id(self, name: str, country_id: int) -> Optional[CitiesOrm]:
        """
        Получить город по названию и ID страны.
        
        Args:
            name: Название города
            country_id: ID страны
            
        Returns:
            ORM объект города или None, если не найдено
        """
        from sqlalchemy.orm import selectinload
        
        query = select(self.model).options(
            selectinload(self.model.country)
        ).where(
            self.model.name == name,
            self.model.country_id == country_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name_case_insensitive(self, name: str) -> Optional[CitiesOrm]:
        """
        Получить город по названию (без учета регистра).
        
        Args:
            name: Название города (может быть в любом регистре)
            
        Returns:
            ORM объект города или None, если не найдено
        """
        from sqlalchemy import func
        
        query = select(self.model).where(
            func.lower(self.model.name) == func.lower(name)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

