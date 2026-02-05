"""
Сервис для работы с бронированиями.

Содержит бизнес-логику создания, удаления и получения бронирований.
"""

from datetime import date

from sqlalchemy import select

from src.exceptions.domain import DateValidationError, EntityNotFoundError, PermissionError, RoomAvailabilityError
from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm
from src.schemas.bookings import SchemaBooking
from src.services.base import BaseService


class BookingsService(BaseService):
    """
    Сервис для работы с бронированиями.

    Инкапсулирует бизнес-логику:
    - Валидация дат бронирования
    - Проверка доступности номеров
    - Расчет цены бронирования
    - Проверка прав доступа
    """

    async def create_booking(self, room_id: int, user_id: int, date_from: date, date_to: date) -> SchemaBooking:
        """
        Создать бронирование с полной валидацией.

        Выполняет все проверки и создает бронирование:
        - Проверяет существование номера
        - Проверяет корректность дат
        - Проверяет доступность номера (с учетом quantity)
        - Рассчитывает цену
        - Создает бронирование

        Args:
            room_id: ID номера
            user_id: ID пользователя
            date_from: Дата заезда
            date_to: Дата выезда

        Returns:
            Созданное бронирование (Pydantic схема)

        Raises:
            EntityNotFoundError: Если номер не найден
            DateValidationError: Если даты некорректны
            RoomAvailabilityError: Если номер недоступен
        """
        # Проверяем существование номера
        room_query = select(RoomsOrm).where(RoomsOrm.id == room_id)
        room_result = await self.session.execute(room_query)
        room = room_result.scalar_one_or_none()

        if room is None:
            raise EntityNotFoundError("Номер", entity_id=room_id)

        # Проверяем корректность дат
        if date_from >= date_to:
            raise DateValidationError("Дата заезда должна быть раньше даты выезда")

        # Проверяем доступность номера (с учетом quantity)
        is_available = await self.bookings_repo.is_room_available(room_id=room_id, date_from=date_from, date_to=date_to)

        if not is_available:
            raise RoomAvailabilityError("Все номера данного типа уже забронированы на указанные даты")

        # Рассчитываем общую цену
        try:
            total_price = BookingsOrm.calculate_total_price(
                room_price_per_night=room.price, date_from=date_from, date_to=date_to
            )
        except ValueError as e:
            raise DateValidationError(str(e))

        # Создаем бронирование
        booking_data = {
            "room_id": room_id,
            "user_id": user_id,
            "date_from": date_from,
            "date_to": date_to,
            "price": total_price,
        }

        return await self.bookings_repo.create(**booking_data)

    async def delete_booking(self, booking_id: int, user_id: int) -> bool:
        """
        Удалить бронирование с проверкой прав доступа.

        Пользователь может удалить только свои бронирования.

        Args:
            booking_id: ID бронирования для удаления
            user_id: ID пользователя, который пытается удалить

        Returns:
            True если бронирование удалено, False если не найдено

        Raises:
            PermissionError: Если бронирование не принадлежит пользователю
        """
        # Проверяем существование бронирования
        booking = await self.bookings_repo.get_by_id(booking_id)
        if booking is None:
            return False

        # Проверяем, что бронирование принадлежит текущему пользователю
        if booking.user_id != user_id:
            raise PermissionError("Недостаточно прав для удаления этого бронирования")

        # Удаляем бронирование
        deleted = await self.bookings_repo.delete(booking_id)
        return deleted

    async def get_user_bookings(self, user_id: int, page: int, per_page: int) -> list[SchemaBooking]:
        """
        Получить список бронирований пользователя с пагинацией.

        Args:
            user_id: ID пользователя
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице

        Returns:
            Список бронирований пользователя
        """
        return await self.bookings_repo.get_paginated(page=page, per_page=per_page, user_id=user_id)

    async def get_all_bookings(self, page: int, per_page: int) -> list[SchemaBooking]:
        """
        Получить список всех бронирований с пагинацией.

        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество элементов на странице

        Returns:
            Список всех бронирований
        """
        return await self.bookings_repo.get_paginated(page=page, per_page=per_page)
