"""
Мапперы для преобразования исключений между слоями.

Преобразует доменные исключения (DomainException) в API исключения (HTTPException).
"""

from fastapi import HTTPException

from src.exceptions.api import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from src.exceptions.base import DomainException


def domain_to_api_exception(exc: DomainException) -> HTTPException:
    """
    Преобразовать доменное исключение в HTTPException.

    Маппинг доменных исключений на соответствующие HTTP статус-коды:
    - EntityNotFoundError → 404 Not Found
    - EntityAlreadyExistsError → 409 Conflict
    - ValidationError → 400 Bad Request
    - PermissionError → 403 Forbidden
    - Остальные DomainException → 400 Bad Request

    Args:
        exc: Доменное исключение

    Returns:
        HTTPException с соответствующим статус-кодом
    """
    from src.exceptions.domain import (
        EntityAlreadyExistsError,
        EntityNotFoundError,
        PermissionError,
        ValidationError,
    )

    if isinstance(exc, EntityNotFoundError):
        return NotFoundError(str(exc))
    elif isinstance(exc, EntityAlreadyExistsError):
        return ConflictError(str(exc))
    elif isinstance(exc, ValidationError):
        return BadRequestError(str(exc))
    elif isinstance(exc, PermissionError):
        return ForbiddenError(str(exc))
    else:
        return BadRequestError(str(exc))
