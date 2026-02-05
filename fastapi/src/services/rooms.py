"""
Сервис для работы с номерами.

Содержит бизнес-логику создания, обновления и удаления номеров.
"""

from typing import Any

from src.exceptions.domain import EntityNotFoundError, ValidationError
from src.schemas.rooms import SchemaRoom
from src.services.base import BaseService


class RoomsService(BaseService):
    """
    Сервис для работы с номерами.

    Инкапсулирует бизнес-логику:
    - Проверка существования отеля
    - Валидация и обработка удобств
    - Проверка принадлежности номера отелю
    """

    async def create_room(
        self, hotel_id: int, room_data: dict[str, Any], facility_ids: list[int] | None = None
    ) -> SchemaRoom:
        """
        Создать номер в отеле с валидацией.

        Args:
            hotel_id: ID отеля
            room_data: Данные номера (без facility_ids)
            facility_ids: Список ID удобств (опционально)

        Returns:
            Созданный номер (Pydantic схема)

        Raises:
            EntityNotFoundError: Если отель не найден или удобство не найдено
        """
        # Проверяем существование отеля
        hotel = await self.hotels_repo.get_by_id(hotel_id)
        if hotel is None:
            raise EntityNotFoundError("Отель", entity_id=hotel_id)

        # Добавляем hotel_id в данные
        room_data["hotel_id"] = hotel_id

        # Создаем номер
        created_room = await self.rooms_repo.create(**room_data)
        room_id = created_room.id

        # Если передан список удобств, валидируем и добавляем их
        if facility_ids is not None:
            await self._validate_and_add_facilities(room_id=room_id, facility_ids=facility_ids)

        return created_room

    async def update_room(
        self, hotel_id: int, room_id: int, room_data: dict[str, Any], facility_ids: list[int] | None = None
    ) -> SchemaRoom:
        """
        Обновить номер с валидацией.

        Args:
            hotel_id: ID отеля
            room_id: ID номера для обновления
            room_data: Данные для обновления (без facility_ids)
            facility_ids: Список ID удобств (опционально, None = не изменять, [] = очистить)

        Returns:
            Обновленный номер (Pydantic схема)

        Raises:
            EntityNotFoundError: Если отель или номер не найдены, номер не принадлежит отелю или удобство не найдено
            ValidationError: Если номер не принадлежит указанному отелю
        """
        # Проверяем существование отеля
        hotel = await self.hotels_repo.get_by_id(hotel_id)
        if hotel is None:
            raise EntityNotFoundError("Отель", entity_id=hotel_id)

        # Проверяем существование номера
        existing_room = await self.rooms_repo.get_by_id(room_id)
        if existing_room is None:
            raise EntityNotFoundError("Номер", entity_id=room_id)

        # Проверяем принадлежность номера отелю
        if existing_room.hotel_id != hotel_id:
            raise ValidationError("Номер не принадлежит указанному отелю")

        # Добавляем hotel_id в данные
        room_data["hotel_id"] = hotel_id

        # Обновляем номер
        updated_room = await self.rooms_repo.edit(id=room_id, **room_data)
        if updated_room is None:
            raise EntityNotFoundError("Номер", entity_id=room_id)

        # Обрабатываем удобства
        if facility_ids is not None:
            # Эффективное обновление: удаляет только отсутствующие, добавляет только новые
            await self._validate_and_update_facilities(room_id=room_id, facility_ids=facility_ids)

        return updated_room

    async def partial_update_room(self, hotel_id: int, room_id: int, room_data: dict[str, Any]) -> SchemaRoom:
        """
        Частично обновить номер с валидацией.

        Args:
            hotel_id: ID отеля
            room_id: ID номера для обновления
            room_data: Данные для обновления (только изменяемые поля)

        Returns:
            Обновленный номер (Pydantic схема)

        Raises:
            EntityNotFoundError: Если отель или номер не найдены
            ValidationError: Если номер не принадлежит отелю
        """
        # Проверяем существование отеля
        hotel = await self.hotels_repo.get_by_id(hotel_id)
        if hotel is None:
            raise EntityNotFoundError("Отель", entity_id=hotel_id)

        # Проверяем существование номера
        existing_room = await self.rooms_repo.get_by_id(room_id)
        if existing_room is None:
            raise EntityNotFoundError("Номер", entity_id=room_id)

        # Проверяем принадлежность номера отелю
        if existing_room.hotel_id != hotel_id:
            raise ValidationError("Номер не принадлежит указанному отелю")

        # Обновляем номер
        updated_room = await self.rooms_repo.edit(id=room_id, **room_data)
        if updated_room is None:
            raise EntityNotFoundError("Номер", entity_id=room_id)

        return updated_room

    async def delete_room(self, hotel_id: int, room_id: int) -> bool:
        """
        Удалить номер с валидацией.

        Args:
            hotel_id: ID отеля
            room_id: ID номера для удаления

        Returns:
            True если номер удален, False если не найден

        Raises:
            EntityNotFoundError: Если отель не найден
            ValidationError: Если номер не принадлежит отелю
        """
        # Проверяем существование отеля
        hotel = await self.hotels_repo.get_by_id(hotel_id)
        if hotel is None:
            raise EntityNotFoundError("Отель", entity_id=hotel_id)

        # Проверяем существование номера
        room = await self.rooms_repo.get_by_id(room_id)
        if room is None:
            return False

        # Проверяем принадлежность номера отелю
        if room.hotel_id != hotel_id:
            raise ValidationError("Номер не принадлежит указанному отелю")

        # Удаляем номер
        deleted = await self.rooms_repo.delete(room_id)
        return deleted

    async def _validate_and_add_facilities(self, room_id: int, facility_ids: list[int]) -> None:
        """
        Валидировать существование удобств и добавить их к номеру.

        Args:
            room_id: ID номера
            facility_ids: Список ID удобств

        Raises:
            EntityNotFoundError: Если какое-либо удобство не найдено
        """
        # Проверяем существование всех удобств
        for facility_id in facility_ids:
            facility = await self.facilities_repo.get_by_id(facility_id)
            if facility is None:
                raise EntityNotFoundError("Удобство", entity_id=facility_id)

        # Добавляем связи
        for facility_id in facility_ids:
            await self.rooms_repo.add_facility(room_id, facility_id)

    async def _validate_and_update_facilities(self, room_id: int, facility_ids: list[int]) -> None:
        """
        Валидировать существование удобств и обновить связи номера.

        Args:
            room_id: ID номера
            facility_ids: Список ID удобств (пустой список = очистить все)

        Raises:
            EntityNotFoundError: Если какое-либо удобство не найдено
        """
        # Если передан пустой список, очищаем все связи
        if len(facility_ids) == 0:
            await self.rooms_repo.update_room_facilities(room_id, [])
            return

        # Проверяем существование всех удобств
        for facility_id in facility_ids:
            facility = await self.facilities_repo.get_by_id(facility_id)
            if facility is None:
                raise EntityNotFoundError("Удобство", entity_id=facility_id)

        # Эффективное обновление: удаляет только отсутствующие, добавляет только новые
        await self.rooms_repo.update_room_facilities(room_id, facility_ids)
