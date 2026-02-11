from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy.exc import DatabaseError

from src.api import (
    auth_router,
    bookings_router,
    cities_router,
    countries_router,
    facilities_router,
    health_router,
    hotels_router,
    images_router,
    rooms_router,
    users_router,
)
from src.config import settings
from src.exceptions.base import DomainException
from src.metrics.setup import setup_prometheus_instrumentator
from src.middleware.exception_handler import (
    database_exception_handler,
    domain_exception_handler,
    general_exception_handler,
)
from src.middleware.http_logging import HTTPLoggingMiddleware
from src.middleware.rate_limiting import setup_rate_limiting
from src.utils.logger import get_logger, setup_logging
from src.utils.startup import shutdown_handler, startup_handler

log_file_name = "app_test.log" if settings.DB_NAME == "test" else "app.log"
setup_logging(log_file_name=log_file_name)

logger = get_logger(__name__)
logger.info(
    f"Приложение запущено. Режим: {'тестовый' if settings.DB_NAME == 'test' else 'основной'}. Логирование в файл: {log_file_name}"
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Lifespan события для FastAPI - выполняется при старте и остановке приложения."""
    await startup_handler()
    yield
    await shutdown_handler()


API_DESCRIPTION = """
## 🏨 Shum Booking API

RESTful API для сервиса бронирования отелей с полным функционалом управления бронированиями, отелями, номерами и пользователями.

### ✨ Основные возможности

- **Аутентификация и авторизация**: JWT токены с refresh механизмом
- **Управление отелями**: CRUD операции для отелей, номеров, удобств
- **Бронирования**: Создание и управление бронированиями с автоматическим расчетом цены
- **География**: Управление странами и городами
- **Мониторинг**: Health checks, метрики Prometheus, структурированное логирование
- **Безопасность**: Rate limiting, HTTPS, защита от основных уязвимостей

### 🔐 Аутентификация

API использует JWT токены для аутентификации. Токен можно передать:
- В HTTP-only cookie `access_token`
- В заголовке `Authorization: Bearer <token>`

### 📊 Технологии

- **Backend**: FastAPI, Python 3.11
- **База данных**: PostgreSQL 16
- **Кэш**: Redis 7
- **Очереди**: Celery
- **Деплой**: Kubernetes (K3s)

### 📝 Примечания

- Все даты в формате `YYYY-MM-DD`
- Все ответы в формате JSON
- Поддержка пагинации для списковых эндпоинтов
- Кэширование результатов в Redis
- Rate limiting для защиты от злоупотреблений
"""

app = FastAPI(
    title="Shum Booking API",
    description=API_DESCRIPTION,
    version="1.0.1",
    lifespan=lifespan,
    root_path=settings.ROOT_PATH if settings.ROOT_PATH else None,  # Для работы за прокси с префиксом пути
    contact={
        "name": "Shum Booking API Support",
        "email": "support@async-black.ru",
    },
    license_info={
        "name": "MIT",
    },
    terms_of_service="https://async-black.ru/terms",
    openapi_tags=[
        {
            "name": "Система",
            "description": "Эндпоинты для мониторинга состояния приложения: health checks, readiness, liveness, метрики Prometheus",
        },
        {
            "name": "Аутентификация",
            "description": "Регистрация новых пользователей, вход в систему, обновление токенов, выход. Использует JWT токены с refresh механизмом.",
        },
        {
            "name": "Пользователи",
            "description": "Управление пользователями: получение списка, просмотр профиля, обновление данных, удаление",
        },
        {
            "name": "Отели",
            "description": "Управление отелями: создание, обновление, удаление, поиск с фильтрацией и сортировкой. Поиск отелей с доступными номерами на период.",
        },
        {
            "name": "Номера",
            "description": "Управление номерами отелей: создание, обновление, удаление, просмотр доступных номеров на период с учетом бронирований",
        },
        {
            "name": "Бронирования",
            "description": "Управление бронированиями: создание новых бронирований с автоматическим расчетом цены, просмотр своих бронирований, отмена",
        },
        {
            "name": "Удобства",
            "description": "Управление удобствами номеров: Wi-Fi, кондиционер, мини-бар и другие. Связывание удобств с номерами",
        },
        {
            "name": "Изображения отелей",
            "description": "Загрузка и управление изображениями отелей. Поддержка различных форматов изображений",
        },
        {
            "name": "Страны",
            "description": "Управление странами: создание, обновление, удаление. Используется для организации географической структуры",
        },
        {
            "name": "Города",
            "description": "Управление городами: создание, обновление, удаление. Связь со странами для организации географии",
        },
    ],
)


def custom_openapi():
    """Кастомная конфигурация OpenAPI схемы для улучшения внешнего вида Swagger UI"""
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        contact=app.contact,
        license_info=app.license_info,
        terms_of_service=app.terms_of_service,
    )

    # Добавляем externalDocs для ссылки на документацию
    openapi_schema["externalDocs"] = {
        "description": "Документация проекта",
        "url": "https://github.com/arsendavydov/shum-booking",
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Регистрируем middleware ПЕРЕД роутерами
if settings.DB_NAME != "test":
    app.add_middleware(HTTPLoggingMiddleware)
    logger.info("HTTPLoggingMiddleware добавлен в приложение")
    setup_rate_limiting(app)
    logger.info("Rate Limiting настроен")
else:
    logger.info("HTTPLoggingMiddleware НЕ добавлен (тестовый режим)")
    # Rate limiting можно включить в тестах через переменную окружения RATE_LIMIT_ENABLED_IN_TESTS
    import os

    if os.getenv("RATE_LIMIT_ENABLED_IN_TESTS", "false").lower() == "true":
        setup_rate_limiting(app)
        logger.info("Rate Limiting настроен для тестов (RATE_LIMIT_ENABLED_IN_TESTS=true)")
    else:
        logger.info(
            "Rate Limiting НЕ настроен (тестовый режим, используйте RATE_LIMIT_ENABLED_IN_TESTS=true для включения)"
        )

app.add_exception_handler(DatabaseError, database_exception_handler)
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

setup_prometheus_instrumentator(app)
if settings.DB_NAME != "test":
    logger.info("Prometheus instrumentator настроен")

app.include_router(health_router, tags=["Система"])
app.include_router(auth_router, prefix="/auth", tags=["Аутентификация"])
app.include_router(users_router, prefix="/users", tags=["Пользователи"])
app.include_router(hotels_router, prefix="/hotels", tags=["Отели"])
app.include_router(rooms_router, prefix="/hotels/{hotel_id}/rooms", tags=["Номера"])
app.include_router(bookings_router, prefix="/bookings", tags=["Бронирования"])
app.include_router(facilities_router, prefix="/facilities", tags=["Удобства"])
app.include_router(images_router, prefix="/images", tags=["Изображения отелей"])
app.include_router(countries_router, prefix="/countries", tags=["Страны"])
app.include_router(cities_router, prefix="/cities", tags=["Города"])

if __name__ == "__main__":
    uvicorn.run(app="src.main:app", host="127.0.0.1", port=8000, reload=True)
