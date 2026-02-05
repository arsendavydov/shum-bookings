"""
Модуль исключений приложения.

Содержит иерархию исключений для разных слоев:
- Domain exceptions - бизнес-логика (сервисы)
- Repository exceptions - работа с БД (репозитории)
- API exceptions - HTTP слой (API endpoints)
"""

from src.exceptions.api import APIException, BadRequestError, ConflictError, NotFoundError
from src.exceptions.base import BaseAppException, DomainException, RepositoryException
from src.exceptions.domain import (
    BookingValidationError,
    DateValidationError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PermissionError,
    RoomAvailabilityError,
    ValidationError,
)
from src.exceptions.mappers import domain_to_api_exception

__all__ = [
    "APIException",
    "BadRequestError",
    "BaseAppException",
    "BookingValidationError",
    "ConflictError",
    "DateValidationError",
    "DomainException",
    "EntityAlreadyExistsError",
    "EntityNotFoundError",
    "NotFoundError",
    "PermissionError",
    "RepositoryException",
    "RoomAvailabilityError",
    "ValidationError",
    "domain_to_api_exception",
]
