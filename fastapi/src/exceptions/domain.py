"""
Доменные исключения (бизнес-логика).

Используются в сервисном слое для инкапсуляции бизнес-правил.
"""

from src.exceptions.base import DomainException


class EntityNotFoundError(DomainException):
    """
    Сущность не найдена.

    Используется когда запрашиваемая сущность не существует в БД.
    """

    def __init__(
        self,
        entity_name: str,
        entity_id: int | None = None,
        field_name: str | None = None,
        field_value: str | None = None,
    ) -> None:
        """
        Инициализация исключения.

        Args:
            entity_name: Название сущности (например, "Отель", "Номер")
            entity_id: ID сущности (опционально)
            field_name: Название поля для поиска (опционально)
            field_value: Значение поля для поиска (опционально)
        """
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.field_name = field_name
        self.field_value = field_value

        if field_name and field_value:
            message = f"{entity_name} с {field_name} '{field_value}' не найден"
        elif entity_id:
            message = f"{entity_name} с ID {entity_id} не найден"
        else:
            message = f"{entity_name} не найден"

        super().__init__(message)


class EntityAlreadyExistsError(DomainException):
    """
    Сущность уже существует.

    Используется при попытке создать сущность с уже существующим уникальным значением.
    """

    def __init__(self, entity_name: str, field_name: str, field_value: str) -> None:
        """
        Инициализация исключения.

        Args:
            entity_name: Название сущности (например, "Отель", "Страна")
            field_name: Название поля с конфликтом (например, "title", "iso_code")
            field_value: Значение поля, которое уже существует
        """
        self.entity_name = entity_name
        self.field_name = field_name
        self.field_value = field_value
        message = f"{entity_name} с {field_name} '{field_value}' уже существует"
        super().__init__(message)


class ValidationError(DomainException):
    """
    Ошибка валидации бизнес-правил.

    Базовый класс для всех ошибок валидации.
    """

    pass


class BookingValidationError(ValidationError):
    """
    Ошибка валидации бронирования.

    Используется для ошибок, связанных с валидацией бронирований.
    """

    pass


class DateValidationError(BookingValidationError):
    """
    Ошибка валидации дат.

    Используется когда даты бронирования некорректны.
    """

    pass


class RoomAvailabilityError(BookingValidationError):
    """
    Номер недоступен для бронирования.

    Используется когда все номера данного типа уже забронированы.
    """

    pass


class PermissionError(DomainException):
    """
    Ошибка прав доступа.

    Используется когда пользователь пытается выполнить действие, на которое у него нет прав.
    """

    pass
