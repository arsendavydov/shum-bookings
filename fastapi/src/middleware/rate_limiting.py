"""
Middleware для rate limiting (ограничение количества запросов).

Защищает API от brute-force атак и DDoS.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.config import settings

# Создаем экземпляр limiter
# Используем get_remote_address для определения IP клиента
limiter = Limiter(key_func=get_remote_address)


def setup_rate_limiting(app):
    """
    Настроить rate limiting для приложения.

    Args:
        app: Экземпляр FastAPI приложения
    """
    if not settings.RATE_LIMIT_ENABLED:
        return

    # Подключаем limiter к приложению
    app.state.limiter = limiter

    # Регистрируем обработчик ошибок rate limiting
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Экспортируем декоратор для использования в роутерах
# В slowapi декоратор работает с Request объектом через app.state.limiter
def rate_limit(limit_value: str):
    """
    Декоратор для ограничения количества запросов к эндпоинту.

    Args:
        limit_value: Строка с лимитом, например "5/minute" или "60/hour"

    Returns:
        Декоратор для применения к эндпоинту
    """
    # Если rate limiting отключен, возвращаем пустой декоратор
    # Проверяем также, не в тестовом режиме ли мы (если DB_NAME == "test" и RATE_LIMIT_ENABLED_IN_TESTS не установлен)
    import os
    
    is_test_mode = settings.DB_NAME == "test"
    rate_limit_enabled_in_tests = os.getenv("RATE_LIMIT_ENABLED_IN_TESTS", "false").lower() == "true"
    
    if not settings.RATE_LIMIT_ENABLED or (is_test_mode and not rate_limit_enabled_in_tests):
        def noop_decorator(func):
            return func
        return noop_decorator
    
    return limiter.limit(limit_value)

