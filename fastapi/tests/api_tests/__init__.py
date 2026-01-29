# Экспорт переменных из conftest для удобного импорта в тестах
from tests.conftest import (
    TEST_PASSWORD,
    TEST_EXAMPLE_EMAIL_DOMAIN
)

__all__ = [
    "TEST_PASSWORD",
    "TEST_EXAMPLE_EMAIL_DOMAIN"
]

