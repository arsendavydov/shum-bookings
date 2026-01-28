from fastapi import HTTPException
from typing import Optional, TypeVar, Generic, Callable, Awaitable
from src.utils.db_manager import DBManager

T = TypeVar('T')


async def get_or_404(
    repo_get_method: Callable[[int], Awaitable[Optional[T]]],
    entity_id: int,
    entity_name: str
) -> T:
    """
    Получить сущность по ID или выбросить 404 если не найдена.
    
    Args:
        repo_get_method: Метод репозитория для получения сущности (например, repo.get_by_id)
        entity_id: ID сущности
        entity_name: Название сущности для сообщения об ошибке (например, "Отель", "Пользователь")
        
    Returns:
        Найденная сущность
        
    Raises:
        HTTPException: 404 если сущность не найдена
    """
    entity = await repo_get_method(entity_id)
    if entity is None:
        raise HTTPException(
            status_code=404,
            detail=f"{entity_name} не найден" if entity_name.endswith(("а", "я", "ь")) else f"{entity_name} не найдено"
        )
    return entity

