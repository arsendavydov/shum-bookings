"""
Исключения API слоя.

Используются в API endpoints для HTTP ошибок.
"""

from fastapi import HTTPException, status


class APIException(HTTPException):
    """
    Базовое исключение API слоя.

    Наследуется от HTTPException для совместимости с FastAPI.
    """

    def __init__(self, status_code: int, detail: str) -> None:
        """
        Инициализация исключения.

        Args:
            status_code: HTTP статус-код
            detail: Сообщение об ошибке
        """
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(APIException):
    """
    404 Not Found.

    Используется когда запрашиваемый ресурс не найден.
    """

    def __init__(self, detail: str) -> None:
        """
        Инициализация исключения.

        Args:
            detail: Сообщение об ошибке
        """
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(APIException):
    """
    409 Conflict.

    Используется при конфликтах данных (например, дубликаты).
    """

    def __init__(self, detail: str) -> None:
        """
        Инициализация исключения.

        Args:
            detail: Сообщение об ошибке
        """
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class BadRequestError(APIException):
    """
    400 Bad Request.

    Используется для ошибок валидации и некорректных запросов.
    """

    def __init__(self, detail: str) -> None:
        """
        Инициализация исключения.

        Args:
            detail: Сообщение об ошибке
        """
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ForbiddenError(APIException):
    """
    403 Forbidden.

    Используется когда у пользователя нет прав для выполнения действия.
    """

    def __init__(self, detail: str) -> None:
        """
        Инициализация исключения.

        Args:
            detail: Сообщение об ошибке
        """
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
