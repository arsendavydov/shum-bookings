"""
Примеры для эндпоинтов пользователей.
"""

# Примеры для PUT /users/{user_id}
UPDATE_USER_BODY_EXAMPLES = {
    "1": {
        "summary": "Обновить пользователя",
        "value": {
            "email": "ivan.petrov@async-black.ru",
            "hashed_password": "$2b$12$...",
            "first_name": "Иван",
            "last_name": "Петров",
            "telegram_id": 123456789,
            "pachca_id": 987654321,
        },
    }
}

# Примеры для PATCH /users/{user_id}
PATCH_USER_BODY_EXAMPLES = {
    "1": {"summary": "Обновить пользователя", "value": {"first_name": "Иван"}},
}
