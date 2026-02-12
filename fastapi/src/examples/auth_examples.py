"""
Примеры для эндпоинтов аутентификации.
"""

# Примеры для POST /auth/register
REGISTER_BODY_EXAMPLES = {
    "1": {
        "summary": "Регистрация",
        "value": {"email": "ivan.petrov@async-black.ru", "password": "TestPassword123!"},
    }
}

# Примеры для POST /auth/login
LOGIN_BODY_EXAMPLES = {
    "1": {
        "summary": "Вход",
        "value": {"email": "ivan.petrov@async-black.ru", "password": "TestPassword123!"},
    }
}
