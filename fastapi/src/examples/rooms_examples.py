"""
Примеры для эндпоинтов номеров.
"""

# Примеры для POST /hotels/{hotel_id}/rooms
CREATE_ROOM_BODY_EXAMPLES = {
    "1": {
        "summary": "Создать номер",
        "value": {
            "title": "Стандартный номер",
            "description": "Уютный стандартный номер с современным дизайном",
            "price": 3000,
            "quantity": 5,
            "facility_ids": [120, 121, 122],
        },
    }
}

# Примеры для PUT /hotels/{hotel_id}/rooms/{room_id}
UPDATE_ROOM_BODY_EXAMPLES = {
    "1": {
        "summary": "Полное обновление номера",
        "value": {
            "title": "Улучшенный номер",
            "description": "Обновленное описание номера",
            "price": 4500,
            "quantity": 4,
            "facility_ids": [120, 121, 122, 123],
        },
    }
}

# Примеры для PATCH /hotels/{hotel_id}/rooms/{room_id}
PATCH_ROOM_BODY_EXAMPLES = {
    "1": {"summary": "Обновить номер", "value": {"price": 3500}},
}
