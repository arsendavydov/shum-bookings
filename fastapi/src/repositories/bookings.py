from typing import List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.repositories.base import BaseRepository
from src.repositories.utils import apply_pagination, check_date_overlap
from src.models.bookings import BookingsOrm
from src.schemas.bookings import SchemaBooking
from src.repositories.mappers.bookings_mapper import BookingsMapper


class BookingsRepository(BaseRepository[BookingsOrm]):
    """
    Репозиторий для работы с бронированиями.
    
    Наследует базовые CRUD методы и добавляет специфичные методы
    для работы с бронированиями.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория бронирований.
        
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        super().__init__(session, BookingsOrm)
    
    def _to_schema(self, orm_obj: BookingsOrm) -> SchemaBooking:
        """
        Преобразовать ORM объект бронирования в Pydantic схему.
        
        Args:
            orm_obj: ORM объект бронирования
            
        Returns:
            Pydantic схема SchemaBooking
        """
        return BookingsMapper.to_schema(orm_obj)
    
    async def has_conflicting_bookings(
        self,
        room_id: int,
        date_from: date,
        date_to: date,
        exclude_booking_id: int | None = None
    ) -> bool:
        """
        Проверить, есть ли конфликтующие бронирования для номера на указанные даты.
        
        Два периода пересекаются, если:
        - date_from нового бронирования < date_to существующего И
        - date_to нового бронирования > date_from существующего
        
        Args:
            room_id: ID номера
            date_from: Дата заезда нового бронирования
            date_to: Дата выезда нового бронирования
            exclude_booking_id: ID бронирования для исключения из проверки (при обновлении)
            
        Returns:
            True если есть конфликтующие бронирования, False иначе
        """
        query = select(self.model).where(
            and_(
                self.model.room_id == room_id,
                self.model.date_from < date_to,
                self.model.date_to > date_from
            )
        )
        
        if exclude_booking_id is not None:
            query = query.where(self.model.id != exclude_booking_id)
        
        result = await self.session.execute(query)
        conflicting_bookings = result.scalars().all()
        
        return len(conflicting_bookings) > 0
    
    async def get_paginated(
        self,
        page: int,
        per_page: int,
        user_id: int | None = None
    ) -> List[SchemaBooking]:
        """
        Получить список бронирований с пагинацией и фильтрацией.
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            user_id: Опциональный фильтр по ID пользователя
            
        Returns:
            Список бронирований (Pydantic схемы)
        """
        query = select(self.model)
        
        # Применяем фильтр по user_id, если указан
        if user_id is not None:
            query = query.where(self.model.user_id == user_id)
        
        # Применяем сортировку и пагинацию
        query = query.order_by(self.model.date_from.desc())
        query = apply_pagination(query, page, per_page)
        
        result = await self.session.execute(query)
        orm_objs = list(result.scalars().all())
        
        return [self._to_schema(obj) for obj in orm_objs]

