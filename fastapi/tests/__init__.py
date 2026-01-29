# Экспорт общих переменных и фикстур из conftest для удобного импорта
from tests.conftest import (
    TEST_PASSWORD,
    TEST_EXAMPLE_EMAIL_DOMAIN,
    BASE_URL,
    TEST_PREFIX
)

__all__ = [
    "TEST_PASSWORD",
    "TEST_EXAMPLE_EMAIL_DOMAIN",
    "BASE_URL",
    "TEST_PREFIX"
]

