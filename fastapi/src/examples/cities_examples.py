"""
Примеры для эндпоинтов городов.
"""

# Примеры для POST /cities
CREATE_CITY_BODY_EXAMPLES = {"1": {"summary": "Создать город", "value": {"name": "Москва", "country_id": 1}}}

# Примеры для PUT /cities/{city_id}
UPDATE_CITY_BODY_EXAMPLES = {
    "1": {
        "summary": "Обновить город",
        "value": {"name": "Обновленный Город", "country_id": 1},
    }
}

# Примеры для PATCH /cities/{city_id}
PATCH_CITY_BODY_EXAMPLES = {
    "1": {"summary": "Обновить город", "value": {"name": "Новый Город"}},
}
