from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.repositories.base import BaseRepository
from src.repositories.utils import apply_pagination, apply_text_filter
from src.models.countries import CountriesOrm
from src.schemas.countries import SchemaCountry
from src.repositories.mappers.countries_mapper import CountriesMapper


class CountriesRepository(BaseRepository[CountriesOrm]):
    """
    Репозиторий для работы со странами.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория стран.
        
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        super().__init__(session, CountriesOrm)
    
    def _to_schema(self, orm_obj: CountriesOrm) -> SchemaCountry:
        """
        Преобразовать ORM объект страны в Pydantic схему.
        
        Args:
            orm_obj: ORM объект страны
            
        Returns:
            Pydantic схема SchemaCountry
        """
        return CountriesMapper.to_schema(orm_obj)
    
    async def get_paginated(
        self,
        page: int,
        per_page: int,
        name: Optional[str] = None
    ) -> List[SchemaCountry]:
        """
        Получить список стран с пагинацией и фильтрацией.
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            name: Опциональный фильтр по названию (частичное совпадение, без учета регистра)
            
        Returns:
            Список стран (Pydantic схемы)
        """
        query = select(self.model)
        
        # Применяем фильтр по name, если указан
        if name is not None:
            query = apply_text_filter(query, self.model.name, name)
        
        # Применяем пагинацию
        query = apply_pagination(query, page, per_page)
        
        result = await self.session.execute(query)
        orm_objs = list(result.scalars().all())
        
        return [self._to_schema(obj) for obj in orm_objs]
    
    async def get_by_iso_code(self, iso_code: str) -> Optional[CountriesOrm]:
        """
        Получить страну по ISO коду.
        
        Args:
            iso_code: ISO 3166-1 alpha-2 код страны (2 буквы)
            
        Returns:
            ORM объект страны или None, если не найдено
        """
        query = select(self.model).where(self.model.iso_code == iso_code.upper())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name_case_insensitive(self, name: str) -> Optional[CountriesOrm]:
        """
        Получить страну по названию (без учета регистра).
        
        Args:
            name: Название страны (может быть в любом регистре)
            
        Returns:
            ORM объект страны или None, если не найдено
        """
        from sqlalchemy import func
        
        query = select(self.model).where(
            func.lower(self.model.name) == func.lower(name)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

