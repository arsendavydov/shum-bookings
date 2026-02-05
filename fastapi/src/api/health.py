from datetime import datetime

from fastapi import APIRouter, Response
from sqlalchemy import text

from src.api.dependencies import DBDep
from src.metrics.setup import get_metrics
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Проверка состояния приложения, подключения к БД и Redis",
    tags=["Система"],
)
async def health_check(db: DBDep) -> dict:
    """
    Проверка состояния приложения.

    Returns:
        Словарь со статусом приложения, БД и Redis
    """
    status = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database": "unknown",
        "redis": "unknown",
    }

    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        status["database"] = "connected"
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}", exc_info=True)
        status["database"] = "disconnected"
        status["status"] = "degraded"

    try:
        from src import redis_manager

        is_connected = await redis_manager.check_connection()
        if is_connected:
            status["redis"] = "connected"
        else:
            status["redis"] = "disconnected"
            status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}", exc_info=True)
        status["redis"] = "disconnected"
        status["status"] = "degraded"

    if status["database"] == "disconnected":
        status["status"] = "down"

    return status


@router.get(
    "/ready",
    summary="Readiness check",
    description="Проверка готовности приложения к обработке запросов",
    tags=["Система"],
)
async def readiness_check(db: DBDep) -> dict:
    """
    Проверка готовности приложения.

    Returns:
        Словарь со статусом готовности
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        return {"ready": True, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Приложение не готово: {e}", exc_info=True)
        return {"ready": False, "timestamp": datetime.now().isoformat(), "error": str(e)}


@router.get(
    "/live",
    summary="Liveness check",
    description="Проверка жизнеспособности приложения",
    tags=["Система"],
)
async def liveness_check() -> dict:
    """
    Проверка жизнеспособности приложения.

    Returns:
        Словарь со статусом жизнеспособности
    """
    return {"alive": True, "timestamp": datetime.now().isoformat()}


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Эндпоинт для сбора метрик Prometheus. Возвращает все метрики в формате Prometheus.",
    tags=["Система"],
)
async def metrics() -> Response:
    """
    Получить метрики Prometheus.

    Returns:
        Response с метриками в формате Prometheus (text/plain)
    """
    metrics_data = get_metrics()
    return Response(content=metrics_data, media_type="text/plain; version=0.0.4; charset=utf-8")
