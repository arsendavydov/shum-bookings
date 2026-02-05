"""
Сервис для работы с отелями.

Содержит бизнес-логику создания, обновления и удаления отелей.
"""

from datetime import date, time
from typing import Any

from src.exceptions.domain import EntityAlreadyExistsError, EntityNotFoundError, ValidationError
from src.schemas.hotels import SchemaHotel, SchemaHotelWithRooms
from src.services.base import BaseService


class HotelsService(BaseService):
    """
    Сервис для работы с отелями.

    Инкапсулирует бизнес-логику:
    - Валидация города при создании/обновлении
    - Проверка уникальности названия отеля
    - Установка дефолтных значений времени заезда/выезда
    """

    async def create_hotel(
        self,
        title: str,
        city_name: str,
        address: str,
        postal_code: str | None = None,
        check_in_time: time | None = None,
        check_out_time: time | None = None,
    ) -> SchemaHotel:
        """
        Создать отель с полной валидацией.

        Выполняет все проверки и создает отель:
        - Валидирует существование города по названию (без учета регистра)
        - Проверяет уникальность title
        - Устанавливает дефолтные значения для check_in_time и check_out_time
        - Создает отель

        Args:
            title: Название отеля
            city_name: Название города (без учета регистра)
            address: Адрес отеля
            postal_code: Почтовый индекс (опционально)
            check_in_time: Время заезда (опционально, по умолчанию 14:00)
            check_out_time: Время выезда (опционально, по умолчанию 12:00)

        Returns:
            Созданный отель (Pydantic схема)

        Raises:
            EntityNotFoundError: Если город не найден
            EntityAlreadyExistsError: Если отель с таким title уже существует
        """
        # Валидируем существование города
        city_orm = await self.cities_repo.get_by_name_case_insensitive(city_name)
        if city_orm is None:
            raise EntityNotFoundError("Город", field_name="название", field_value=city_name)

        # Проверяем уникальность title
        if await self.hotels_repo.exists_by_title(title):
            raise EntityAlreadyExistsError("Отель", "название", title)

        # Устанавливаем дефолтные значения
        if check_in_time is None:
            check_in_time = time(14, 0)
        if check_out_time is None:
            check_out_time = time(12, 0)

        # Создаем отель
        hotel_data = {
            "title": title,
            "city_id": city_orm.id,
            "address": address,
            "postal_code": postal_code,
            "check_in_time": check_in_time,
            "check_out_time": check_out_time,
        }

        return await self.hotels_repo.create(**hotel_data)

    async def update_hotel(
        self,
        hotel_id: int,
        title: str,
        city_name: str,
        address: str,
        postal_code: str | None = None,
        check_in_time: time | None = None,
        check_out_time: time | None = None,
    ) -> SchemaHotel:
        """
        Обновить отель с полной валидацией.

        Выполняет все проверки и обновляет отель:
        - Проверяет существование отеля
        - Валидирует существование города по названию (без учета регистра)
        - Проверяет уникальность title (если изменяется)
        - Обновляет отель

        Args:
            hotel_id: ID отеля для обновления
            title: Новое название отеля
            city_name: Название города (без учета регистра)
            address: Новый адрес отеля
            postal_code: Почтовый индекс (опционально)
            check_in_time: Время заезда (опционально)
            check_out_time: Время выезда (опционально)

        Returns:
            Обновленный отель (Pydantic схема)

        Raises:
            EntityNotFoundError: Если отель не найден или город не найден
            EntityAlreadyExistsError: Если отель с таким title уже существует
        """
        # Проверяем существование отеля
        hotel = await self.hotels_repo.get_by_id(hotel_id)
        if hotel is None:
            raise EntityNotFoundError("Отель", entity_id=hotel_id)

        # Валидируем существование города
        city_orm = await self.cities_repo.get_by_name_case_insensitive(city_name)
        if city_orm is None:
            raise EntityNotFoundError("Город", field_name="название", field_value=city_name)

        # Проверяем уникальность title (если изменяется)
        if hotel.title != title and await self.hotels_repo.exists_by_title(title, exclude_hotel_id=hotel_id):
            raise EntityAlreadyExistsError("Отель", "название", title)

        # Обновляем отель
        hotel_data = {
            "title": title,
            "city_id": city_orm.id,
            "address": address,
            "postal_code": postal_code,
            "check_in_time": check_in_time,
            "check_out_time": check_out_time,
        }

        updated_hotel = await self.hotels_repo.edit(id=hotel_id, **hotel_data)
        if updated_hotel is None:
            raise EntityNotFoundError("Отель", entity_id=hotel_id)
        return updated_hotel

    async def partial_update_hotel(
        self,
        hotel_id: int,
        title: str | None = None,
        city_name: str | None = None,
        address: str | None = None,
        postal_code: str | None = None,
        check_in_time: time | None = None,
        check_out_time: time | None = None,
    ) -> SchemaHotel:
        """
        Частично обновить отель с валидацией.

        Выполняет проверки только для изменяемых полей:
        - Проверяет существование отеля
        - Валидирует город (если изменяется)
        - Проверяет уникальность title (если изменяется)
        - Обновляет только указанные поля

        Args:
            hotel_id: ID отеля для обновления
            title: Новое название отеля (опционально)
            city_name: Название города (опционально)
            address: Новый адрес отеля (опционально)
            postal_code: Почтовый индекс (опционально)
            check_in_time: Время заезда (опционально)
            check_out_time: Время выезда (опционально)

        Returns:
            Обновленный отель (Pydantic схема)

        Raises:
            EntityNotFoundError: Если отель не найден или город не найден
            EntityAlreadyExistsError: Если отель с таким title уже существует
        """
        # Проверяем существование отеля
        hotel = await self.hotels_repo.get_by_id(hotel_id)
        if hotel is None:
            raise EntityNotFoundError("Отель", entity_id=hotel_id)

        # Формируем словарь для обновления
        update_data: dict[str, Any] = {}

        if title is not None:
            # Проверяем уникальность title (если изменяется)
            if hotel.title != title and await self.hotels_repo.exists_by_title(title, exclude_hotel_id=hotel_id):
                raise EntityAlreadyExistsError("Отель", "название", title)
            update_data["title"] = title

        if city_name is not None:
            # Валидируем существование города
            city_orm = await self.cities_repo.get_by_name_case_insensitive(city_name)
            if city_orm is None:
                raise EntityNotFoundError("Город", field_name="название", field_value=city_name)
            update_data["city_id"] = city_orm.id

        if address is not None:
            update_data["address"] = address

        if postal_code is not None:
            update_data["postal_code"] = postal_code

        if check_in_time is not None:
            update_data["check_in_time"] = check_in_time

        if check_out_time is not None:
            update_data["check_out_time"] = check_out_time

        # Если нечего обновлять, возвращаем текущий отель
        if not update_data:
            return hotel

        # Обновляем отель
        updated_hotel = await self.hotels_repo.edit(id=hotel_id, **update_data)
        if updated_hotel is None:
            raise EntityNotFoundError("Отель", entity_id=hotel_id)
        return updated_hotel

    async def delete_hotel(self, hotel_id: int) -> bool:
        """
        Удалить отель.

        Args:
            hotel_id: ID отеля для удаления

        Returns:
            True если отель удален, False если не найден

        Raises:
            ValueError: Если отель не найден
        """
        deleted = await self.hotels_repo.delete(hotel_id)
        return deleted

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
        Получить отели с доступными комнатами на указанный период.

        Args:
            date_from: Дата начала периода
            date_to: Дата окончания периода
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице
            hotel_id: Опциональный ID отеля
            title: Опциональный фильтр по названию отеля
            city: Опциональный фильтр по названию города

        Returns:
            Список отелей с комнатами и актуальным количеством свободных номеров

        Raises:
            ValidationError: Если даты некорректны (date_from >= date_to)
        """
        if date_from >= date_to:
            raise ValidationError("Дата начала периода должна быть раньше даты окончания")

        return await self.hotels_repo.get_hotels_with_available_rooms(
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page,
            hotel_id=hotel_id,
            title=title,
            city=city,
        )
