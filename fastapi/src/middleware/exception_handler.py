from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DatabaseError, IntegrityError, OperationalError

from src.exceptions.base import DomainException
from src.exceptions.mappers import domain_to_api_exception
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def database_exception_handler(_request: Request, exc: DatabaseError) -> JSONResponse:
    """
    Обработчик исключений базы данных.

    Обрабатывает ошибки подключения к БД, нарушения целостности данных и другие ошибки SQLAlchemy.
    """
    logger.error(f"Ошибка базы данных: {exc}", exc_info=True)

    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Нарушение целостности данных. Возможно, запись уже существует или нарушены ограничения."
            },
        )

    if isinstance(exc, OperationalError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Сервис базы данных временно недоступен. Попробуйте позже."},
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера при работе с базой данных."},
    )


async def domain_exception_handler(_request: Request, exc: DomainException) -> JSONResponse:
    """
    Обработчик доменных исключений.

    Преобразует доменные исключения (бизнес-логика) в HTTP ответы.
    """
    logger.error(f"Доменное исключение: {exc}", exc_info=True)
    api_exc = domain_to_api_exception(exc)
    return JSONResponse(
        status_code=api_exc.status_code,
        content={"detail": api_exc.detail},
    )


async def general_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """
    Глобальный обработчик всех необработанных исключений.

    Обрабатывает все исключения, которые не были обработаны другими обработчиками.
    """
    logger.error(f"Необработанное исключение: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера."},
    )
