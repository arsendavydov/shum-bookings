"""
Примеры для эндпоинтов стран.
"""

# Примеры для POST /countries
CREATE_COUNTRY_BODY_EXAMPLES = {"1": {"summary": "Создать страну", "value": {"name": "Россия", "iso_code": "RU"}}}

# Примеры для PUT /countries/{country_id}
UPDATE_COUNTRY_BODY_EXAMPLES = {
    "1": {
        "summary": "Обновить страну",
        "value": {"name": "Российская Федерация", "iso_code": "RU"},
    }
}

# Примеры для PATCH /countries/{country_id}
PATCH_COUNTRY_BODY_EXAMPLES = {
    "1": {"summary": "Обновить страну", "value": {"name": "Российская Федерация"}},
}
