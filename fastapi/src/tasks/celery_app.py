import logging
import os

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

from src.utils.logger import JsonFormatter, _use_json_logs, setup_logging

# Инициализируем логирование для Celery
# Используем LOG_LEVEL из переменных окружения
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level=log_level)

# Настраиваем JSON логирование для Celery через сигналы
if _use_json_logs():
    json_formatter = JsonFormatter()
    
    @after_setup_logger.connect
    def setup_celery_logger(logger, *args, **kwargs):
        """Настроить JSON форматтер для Celery logger."""
        for handler in logger.handlers:
            handler.setFormatter(json_formatter)
        # Также применяем к root logger handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.setFormatter(json_formatter)
    
    @after_setup_task_logger.connect
    def setup_celery_task_logger(logger, *args, **kwargs):
        """Настроить JSON форматтер для Celery task logger."""
        for handler in logger.handlers:
            handler.setFormatter(json_formatter)

# Получаем настройки Redis из переменных окружения напрямую
# Не импортируем settings, чтобы избежать ошибок валидации JWT настроек
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

# Создаем celery_app БЕЗ include, чтобы избежать импорта tasks при инициализации
celery_app = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
)

# Автоматически находим и загружаем задачи из модуля tasks
celery_app.autodiscover_tasks(["src.tasks"], force=True)

# Базовая конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Настройка логирования Celery для JSON формата
# Celery будет использовать наш root logger, который уже настроен через setup_logging
# с JsonFormatter, если LOG_FORMAT_JSON=true
if _use_json_logs():
    # Отключаем стандартный форматтер Celery, чтобы использовать наш
    celery_app.conf.worker_log_format = "%(message)s"  # Минимальный формат, JSON добавит JsonFormatter
    celery_app.conf.worker_task_log_format = "%(message)s"
    celery_app.conf.worker_hijack_root_logger = False  # Не перехватываем root logger
