"""
Примеры для эндпоинтов отелей.
"""

# Примеры для POST /hotels
CREATE_HOTEL_BODY_EXAMPLES = {
    "1": {
        "summary": "Создать отель",
        "value": {"title": "Гранд Отель Москва", "city": "Москва", "address": "Тверская улица, дом 3"},
    }
}

# Примеры для PUT /hotels/{hotel_id}
UPDATE_HOTEL_BODY_EXAMPLES = {
    "1": {
        "summary": "Полное обновление отеля",
        "value": {
            "title": "Обновленный Гранд Отель",
            "city": "Москва",
            "address": "Тверская улица, дом 5",
            "postal_code": "101000",
        },
    }
}

# Примеры для PATCH /hotels/{hotel_id}
PATCH_HOTEL_BODY_EXAMPLES = {
    "1": {"summary": "Обновить отель", "value": {"title": "Новое название отеля"}},
}
