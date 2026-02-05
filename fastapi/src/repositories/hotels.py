from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.hotels import HotelsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.hotels_mapper import HotelsMapper
from src.repositories.utils import apply_pagination, apply_text_filter
from src.schemas.hotels import SchemaHotel, SchemaHotelWithRooms


class HotelsRepository(BaseRepository[HotelsOrm]):
    """
    Репозиторий для работы с отелями.

    Наследует базовые CRUD методы и добавляет специфичные методы
    для работы с отелями (фильтрация, пагинация).
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория отелей.

        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        super().__init__(session, HotelsOrm)

    def _to_schema(self, orm_obj: HotelsOrm) -> SchemaHotel:
        """
        Преобразовать ORM объект отеля в Pydantic схему.

        Args:
            orm_obj: ORM объект отеля

        Returns:
            Pydantic схема SchemaHotel
        """
        return HotelsMapper.to_schema(orm_obj)

    async def get_by_title(self, title: str) -> list[SchemaHotel]:
        """
        Получить отели по названию (точное совпадение).

        Args:
            title: Название отеля

        Returns:
            Список отелей (Pydantic схемы)
        """
        from sqlalchemy.orm import selectinload

        from src.models.cities import CitiesOrm

        query = (
            select(self.model)
            .options(selectinload(self.model.city).selectinload(CitiesOrm.country))
            .where(self.model.title == title)
        )
        result = await self.session.execute(query)
        orm_objs = list(result.scalars().all())
        return [self._to_schema(obj) for obj in orm_objs]

    async def get_by_city_id(self, city_id: int) -> list[SchemaHotel]:
        """
        Получить отели по ID города.

        Args:
            city_id: ID города

        Returns:
            Список отелей (Pydantic схемы)
        """
        from sqlalchemy.orm import selectinload

        from src.models.cities import CitiesOrm

        query = (
            select(self.model)
            .options(selectinload(self.model.city).selectinload(CitiesOrm.country))
            .where(self.model.city_id == city_id)
        )
        result = await self.session.execute(query)
        orm_objs = list(result.scalars().all())
        return [self._to_schema(obj) for obj in orm_objs]

    async def get_paginated(
        self,
        page: int,
        per_page: int,
        title: str | None = None,
        city: str | None = None,
        city_id: int | None = None,
        sort_by: str = "id",
        order: str = "asc",
    ) -> list[SchemaHotel]:
        """
        Получить список отелей с пагинацией, фильтрацией и сортировкой.

        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            title: Опциональный фильтр по названию (частичное совпадение, без учета регистра)
            city: Опциональный фильтр по названию города (частичное совпадение, без учета регистра)
            city_id: Опциональный фильтр по ID города
            sort_by: Поле для сортировки ("id", "title", "city") - по умолчанию "id"
            order: Направление сортировки ("asc" или "desc") - по умолчанию "asc"

        Returns:
            Список отелей (Pydantic схемы)
        """
        from sqlalchemy.orm import selectinload

        from src.models.cities import CitiesOrm

        query = select(self.model).options(selectinload(self.model.city).selectinload(CitiesOrm.country))

        # Применяем фильтры
        if title is not None:
            query = apply_text_filter(query, self.model.title, title)
        if city is not None:
            query = query.join(CitiesOrm, self.model.city_id == CitiesOrm.id)
            query = apply_text_filter(query, CitiesOrm.name, city)
        if city_id is not None:
            query = query.where(self.model.city_id == city_id)

        # Применяем сортировку
        sort_field = None
        if sort_by == "title":
            sort_field = self.model.title
        elif sort_by == "city":
            if city is None and city_id is None:
                query = query.join(CitiesOrm, self.model.city_id == CitiesOrm.id)
            sort_field = CitiesOrm.name
        else:  # по умолчанию "id"
            sort_field = self.model.id

        if order.lower() == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

        # Применяем пагинацию
        query = apply_pagination(query, page, per_page)

        result = await self.session.execute(query)
        orm_objs = list(result.scalars().all())

        return [self._to_schema(obj) for obj in orm_objs]

    async def count(self, title: str | None = None, city: str | None = None) -> int:
        """
        Подсчитать количество отелей с учетом фильтров.

        Args:
            title: Опциональный фильтр по названию
            city: Опциональный фильтр по названию города (частичное совпадение, без учета регистра)

        Returns:
            Количество отелей
        """
        from src.models.cities import CitiesOrm

        query = select(func.count(self.model.id))

        if title is not None:
            query = apply_text_filter(query, self.model.title, title)
        if city is not None:
            # Фильтрация по названию города с частичным совпадением без учета регистра
            query = query.join(CitiesOrm, self.model.city_id == CitiesOrm.id)
            query = apply_text_filter(query, CitiesOrm.name, city)

        result = await self.session.execute(query)
        return result.scalar_one() or 0

    async def get_by_id(self, id: int) -> SchemaHotel | None:
        """
        Получить отель по ID с загрузкой связанного города.

        Args:
            id: ID отеля

        Returns:
            Pydantic схема отеля или None, если не найдено
        """
        from sqlalchemy.orm import selectinload

        from src.models.cities import CitiesOrm

        query = (
            select(self.model)
            .options(selectinload(self.model.city).selectinload(CitiesOrm.country))
            .where(self.model.id == id)
        )
        result = await self.session.execute(query)
        orm_obj = result.scalar_one_or_none()

        if orm_obj is None:
            return None

        return self._to_schema(orm_obj)

    async def exists_by_title(self, title: str, exclude_hotel_id: int | None = None) -> bool:
        """
        Проверить существование отеля с указанным названием.

        Args:
            title: Название отеля
            exclude_hotel_id: ID отеля, который нужно исключить из проверки (для обновления)

        Returns:
            True если отель с таким названием существует, False иначе
        """
        return await self.exists_by_field("title", title, exclude_id=exclude_hotel_id)

    async def get_hotels_with_available_rooms(
        self,
        date_from: date,
        date_to: date,
        page: int,
        per_page: int,
        hotel_id: int | None = None,
        title: str | None = None,
        city: str | None = None,
    ) -> list[SchemaHotelWithRooms]:
        """
        Получить отели с доступными комнатами на указанный период с поддержкой пагинации и фильтрации.

        Для каждого отеля возвращается список комнат с актуальным количеством
        свободных номеров на указанный период. Комнаты с quantity=0 не возвращаются.

        Args:
            date_from: Дата начала периода
            date_to: Дата окончания периода
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            hotel_id: Опциональный ID отеля. Если указан, возвращается только этот отель.
            title: Опциональный фильтр по названию отеля (частичное совпадение, без учета регистра)
            city: Опциональный фильтр по названию города (частичное совпадение, без учета регистра)

        Returns:
            Список отелей с комнатами и актуальным количеством свободных номеров
        """
        from sqlalchemy.orm import selectinload

        from src.models.cities import CitiesOrm

        # Формируем запрос для получения отелей
        query = select(self.model).options(selectinload(self.model.city).selectinload(CitiesOrm.country))

        # Применяем фильтры
        if hotel_id is not None:
            query = query.where(self.model.id == hotel_id)
        if title is not None:
            query = apply_text_filter(query, self.model.title, title)
        if city is not None:
            # Фильтрация по названию города с частичным совпадением без учета регистра
            query = query.join(CitiesOrm, self.model.city_id == CitiesOrm.id)
            query = apply_text_filter(query, CitiesOrm.name, city)

        # Применяем пагинацию
        query = apply_pagination(query, page, per_page)

        result = await self.session.execute(query)
        hotels_orm = list(result.scalars().all())

        if not hotels_orm:
            return []

        # Создаем репозиторий комнат для расчета доступности (импортируем локально, чтобы избежать циклических импортов)
        from src.repositories.rooms import RoomsRepository

        rooms_repo = RoomsRepository(self.session)

        # Для каждого отеля получаем комнаты с актуальным количеством
        hotels_with_rooms = []
        for hotel_orm in hotels_orm:
            # Получаем все комнаты отеля с актуальным количеством
            rooms = await rooms_repo.get_rooms_with_availability(
                hotel_id=hotel_orm.id, date_from=date_from, date_to=date_to
            )

            # Преобразуем отель в схему
            hotel_schema = self._to_schema(hotel_orm)

            # Создаем схему отеля с комнатами
            hotel_with_rooms = SchemaHotelWithRooms(
                id=hotel_schema.id,
                title=hotel_schema.title,
                address=hotel_schema.address,
                postal_code=hotel_schema.postal_code,
                check_in_time=hotel_schema.check_in_time,
                check_out_time=hotel_schema.check_out_time,
                city=hotel_schema.city,
                country=hotel_schema.country,
                rooms=rooms,
            )
            hotels_with_rooms.append(hotel_with_rooms)

        return hotels_with_rooms
