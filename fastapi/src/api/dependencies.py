"""
Модуль зависимостей (Dependencies) для FastAPI.

Содержит все функции-зависимости для Dependency Injection:
- Пагинация
- Сессии базы данных
- Репозитории
- Сервисы
- JWT аутентификация
"""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Cookie, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from src.services.bookings import BookingsService
    from src.services.cities import CitiesService
    from src.services.countries import CountriesService
    from src.services.hotels import HotelsService
    from src.services.images import ImagesService
    from src.services.rooms import RoomsService
    from src.services.users import UsersService

from src.repositories.bookings import BookingsRepository
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository
from src.repositories.users import UsersRepository
from src.schemas.users import SchemaUser
from src.services.auth import AuthService
from src.utils.db_manager import DBManager

# ============================================================================
# ПАГИНАЦИЯ
# ============================================================================


class PaginationParams(BaseModel):
    """Модель параметров пагинации."""

    page: int
    per_page: int


def get_pagination_params(
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    per_page: Annotated[int, Query(ge=1, le=20, description="Количество элементов на странице")] = 10,
) -> PaginationParams:
    """
    Dependency для получения параметров пагинации.

    Args:
        page: Номер страницы (по умолчанию 1, должно быть больше или равно 1)
        per_page: Количество элементов на странице (по умолчанию 10, должно быть от 1 до 20 включительно)

    Returns:
        PaginationParams с параметрами пагинации
    """
    return PaginationParams(page=page, per_page=per_page)


PaginationDep = Annotated[PaginationParams, Depends(get_pagination_params)]


# ============================================================================
# СЕССИИ БАЗЫ ДАННЫХ
# ============================================================================


def get_db_manager() -> DBManager:
    """
    Dependency для получения экземпляра DBManager.

    Returns:
        DBManager: Экземпляр менеджера базы данных
    """
    return DBManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных через DBManager.

    Использует DBManager как контекстный менеджер для управления сессией.
    FastAPI автоматически закроет сессию после завершения запроса.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy
    """
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[AsyncSession, Depends(get_db)]


# ============================================================================
# РЕПОЗИТОРИИ - GENERIC ФАБРИКА
# ============================================================================
# Используем generic фабрику для создания функций зависимостей репозиториев
# Это устраняет дублирование кода и упрощает поддержку


def create_repository_dependency(
    get_repo_method: Any, repo_type: type[Any]
) -> tuple[Any, Any]:
    """
    Фабрика для создания функций зависимостей репозиториев.

    Создает две функции:
    1. get_*_repository - для чтения (без commit)
    2. get_*_repository_with_commit - для записи (с автоматическим commit/rollback)

    Args:
        get_repo_method: Метод DBManager для получения репозитория (например, DBManager.get_hotels_repository)
        repo_type: Тип репозитория (для аннотаций типов)

    Returns:
        Tuple из двух функций: (get_repository, get_repository_with_commit)
    """

    async def get_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> Any:
        """Dependency для получения репозитория (только чтение)."""
        return get_repo_method(db)

    async def get_repository_with_commit(
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> AsyncGenerator[Any, None]:
        """Dependency для получения репозитория (запись с commit/rollback)."""
        repo = get_repo_method(db)
        try:
            yield repo
            await DBManager.commit(db)
        except Exception:
            await DBManager.rollback(db)
            raise

    return get_repository, get_repository_with_commit


# Создаем зависимости для репозиториев через фабрику
get_hotels_repository, get_hotels_repository_with_commit = create_repository_dependency(
    DBManager.get_hotels_repository, HotelsRepository
)

get_users_repository, get_users_repository_with_commit = create_repository_dependency(
    DBManager.get_users_repository, UsersRepository
)

get_rooms_repository, get_rooms_repository_with_commit = create_repository_dependency(
    DBManager.get_rooms_repository, RoomsRepository
)


# ============================================================================
# РЕПОЗИТОРИИ - АННОТАЦИИ ДЛЯ РОУТЕРОВ
# ============================================================================
# Эти аннотации позволяют использовать репозитории в роутерах с явной типизацией
# Пример: async def get_hotels(repo: HotelsRepositoryDep) -> List[SchemaHotel]

HotelsRepositoryDep = Annotated[HotelsRepository, Depends(get_hotels_repository)]
HotelsRepositoryDepWrite = Annotated[HotelsRepository, Depends(get_hotels_repository_with_commit)]

UsersRepositoryDep = Annotated[UsersRepository, Depends(get_users_repository)]
UsersRepositoryDepWrite = Annotated[UsersRepository, Depends(get_users_repository_with_commit)]

RoomsRepositoryDep = Annotated[RoomsRepository, Depends(get_rooms_repository)]
RoomsRepositoryDepWrite = Annotated[RoomsRepository, Depends(get_rooms_repository_with_commit)]


get_bookings_repository, get_bookings_repository_with_commit = create_repository_dependency(
    DBManager.get_bookings_repository, BookingsRepository
)

BookingsRepositoryDep = Annotated[BookingsRepository, Depends(get_bookings_repository)]
BookingsRepositoryDepWrite = Annotated[BookingsRepository, Depends(get_bookings_repository_with_commit)]


# ============================================================================
# СЕРВИСЫ
# ============================================================================


def get_auth_service() -> AuthService:
    """
    Dependency для получения экземпляра AuthService.

    Returns:
        Экземпляр AuthService
    """
    return AuthService()


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


# ============================================================================
# СЕРВИСЫ
# ============================================================================


async def get_bookings_service(db: DBDep) -> "BookingsService":
    """
    Dependency для получения сервиса бронирований.

    Args:
        db: Сессия базы данных

    Returns:
        BookingsService: Сервис для работы с бронированиями
    """
    from src.services.bookings import BookingsService

    return BookingsService(db)


BookingsServiceDep = Annotated["BookingsService", Depends(get_bookings_service)]


async def get_hotels_service(db: DBDep) -> "HotelsService":
    """
    Dependency для получения сервиса отелей.

    Args:
        db: Сессия базы данных

    Returns:
        HotelsService: Сервис для работы с отелями
    """
    from src.services.hotels import HotelsService

    return HotelsService(db)


HotelsServiceDep = Annotated["HotelsService", Depends(get_hotels_service)]


async def get_rooms_service(db: DBDep) -> "RoomsService":
    """
    Dependency для получения сервиса номеров.

    Args:
        db: Сессия базы данных

    Returns:
        RoomsService: Сервис для работы с номерами
    """
    from src.services.rooms import RoomsService

    return RoomsService(db)


RoomsServiceDep = Annotated["RoomsService", Depends(get_rooms_service)]


async def get_users_service(db: DBDep) -> "UsersService":
    """
    Dependency для получения сервиса пользователей.

    Args:
        db: Сессия базы данных

    Returns:
        UsersService: Сервис для работы с пользователями
    """
    from src.services.users import UsersService

    return UsersService(db)


UsersServiceDep = Annotated["UsersService", Depends(get_users_service)]


async def get_images_service(db: DBDep) -> "ImagesService":
    """
    Dependency для получения сервиса изображений.

    Args:
        db: Сессия базы данных

    Returns:
        ImagesService: Сервис для работы с изображениями
    """
    from src.services.images import ImagesService

    return ImagesService(db)


ImagesServiceDep = Annotated["ImagesService", Depends(get_images_service)]


async def get_countries_service(db: DBDep) -> "CountriesService":
    """
    Dependency для получения сервиса стран.

    Args:
        db: Сессия базы данных

    Returns:
        CountriesService: Сервис для работы со странами
    """
    from src.services.countries import CountriesService

    return CountriesService(db)


CountriesServiceDep = Annotated["CountriesService", Depends(get_countries_service)]


async def get_cities_service(db: DBDep) -> "CitiesService":
    """
    Dependency для получения сервиса городов.

    Args:
        db: Сессия базы данных

    Returns:
        CitiesService: Сервис для работы с городами
    """
    from src.services.cities import CitiesService

    return CitiesService(db)


CitiesServiceDep = Annotated["CitiesService", Depends(get_cities_service)]


# ============================================================================
# JWT АУТЕНТИФИКАЦИЯ
# ============================================================================
# Цепочка зависимостей для работы с JWT токенами:
# get_token → get_token_payload → get_current_user


async def get_token(
    request: Request, access_token: str | None = Cookie(None, alias="access_token", include_in_schema=False)
) -> str:
    """
    Dependency для получения JWT токена из запроса.

    Проверяет токен в cookie или Authorization header.

    Args:
        request: FastAPI Request объект
        access_token: JWT токен из cookie (опционально)

    Returns:
        str: JWT токен в виде строки

    Raises:
        HTTPException: 401 если токен не предоставлен
    """
    token = access_token

    # Если токена нет в cookie, проверяем Authorization header
    if not token:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split("Bearer ")[1]

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Токен доступа не предоставлен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


TokenDep = Annotated[str, Depends(get_token)]


async def get_token_payload(token: TokenDep, auth_service: AuthServiceDep) -> dict[str, Any]:
    """
    Dependency для получения и валидации payload из JWT токена.

    Декодирует токен и возвращает его payload.
    Использует get_token для получения токена.

    Args:
        token: JWT токен (получается через get_token)
        auth_service: Сервис для работы с JWT

    Returns:
        Dict[str, Any]: Payload токена

    Raises:
        HTTPException: 401 если токен невалиден или истек
    """
    payload = auth_service.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Токен невалиден или истек",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


TokenPayloadDep = Annotated[dict[str, Any], Depends(get_token_payload)]


async def get_current_user(payload: TokenPayloadDep, db: DBDep) -> SchemaUser:
    """
    Dependency для получения текущего авторизованного пользователя.

    Использует валидированный payload токена для получения user_id
    и загрузки пользователя из БД.
    Использует get_token_payload (который использует get_token).

    Args:
        payload: Payload из JWT токена (получается через get_token_payload)
        db: Сессия базы данных

    Returns:
        SchemaUser: Данные текущего пользователя

    Raises:
        HTTPException: 401 если токен невалиден, отсутствует или пользователь не найден
    """
    # Получаем user_id из токена
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=401,
            detail="Токен не содержит идентификатор пользователя",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Невалидный идентификатор пользователя в токене",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Получаем пользователя из БД
    repo = DBManager.get_users_repository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUserDep = Annotated[SchemaUser, Depends(get_current_user)]
