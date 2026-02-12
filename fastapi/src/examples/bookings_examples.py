"""
Примеры для эндпоинтов бронирований.
"""

# Примеры для POST /bookings
CREATE_BOOKING_BODY_EXAMPLES = {
    "1": {
        "summary": "Создать бронирование",
        "value": {"room_id": 508, "date_from": "2025-02-15", "date_to": "2025-02-18"},
    }
}
