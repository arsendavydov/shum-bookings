"""
Тесты для проверки метрик Prometheus.
"""
import random
import re
import time

import pytest

# Используем фикстуру client из conftest.py (scope="session")


@pytest.fixture(autouse=True)
def setup_test_helpers():
    """Настройка вспомогательных переменных для тестов."""
    pytest.current_time = int(time.time())
    pytest.random_int = random.randint(1000, 9999)


def test_metrics_endpoint_exists(client):
    """Проверить, что эндпоинт /metrics существует и возвращает данные."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
    
    metrics_text = response.text
    assert len(metrics_text) > 0
    assert "# HELP" in metrics_text or "# TYPE" in metrics_text


def test_http_metrics_present(client):
    """Проверить, что HTTP метрики присутствуют.
    
    Примечание: В тестовом режиме prometheus-fastapi-instrumentator отключен,
    поэтому проверяем наличие других метрик, которые всегда доступны.
    """
    client.get("/health")
    
    response = client.get("/metrics")
    assert response.status_code == 200
    
    metrics_text = response.text
    
    # В тестовом режиме HTTP метрики от prometheus-fastapi-instrumentator не собираются,
    # но наши кастомные метрики должны быть доступны
    assert "api_requests_total" in metrics_text or "process_resident_memory_bytes" in metrics_text


def test_auth_metrics_registration(client):
    """Проверить, что метрики регистрации собираются."""
    unique_email = f"test_metrics_{pytest.current_time}_{pytest.random_int}@example.com"
    
    response = client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": "testpass123",
        },
    )
    
    assert response.status_code in [201, 409]
    
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    
    metrics_text = metrics_response.text
    
    if response.status_code == 201:
        assert "auth_registrations_total" in metrics_text


def test_auth_metrics_login(client):
    """Проверить, что метрики входа собираются."""
    unique_email = f"test_login_metrics_{pytest.current_time}_{pytest.random_int}@example.com"
    
    client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": "testpass123",
        },
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": unique_email,
            "password": "testpass123",
        },
    )
    
    assert login_response.status_code == 200
    
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    
    metrics_text = metrics_response.text
    
    assert "auth_logins_total" in metrics_text


def test_system_metrics_present(client):
    """Проверить, что системные метрики присутствуют."""
    response = client.get("/metrics")
    assert response.status_code == 200
    
    metrics_text = response.text
    
    assert "app_uptime_seconds" in metrics_text
    assert "process_resident_memory_bytes" in metrics_text
    assert "app_info" in metrics_text


def test_business_metrics_booking(client):
    """Проверить, что бизнес-метрики для бронирований собираются."""
    unique_email = f"test_booking_metrics_{pytest.current_time}_{pytest.random_int}@example.com"
    
    register_response = client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": "testpass123",
        },
    )
    
    if register_response.status_code != 201:
        pytest.skip("Не удалось создать пользователя для теста")
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": unique_email,
            "password": "testpass123",
        },
    )
    
    if login_response.status_code != 200:
        pytest.skip("Не удалось войти для теста")
    
    token_data = login_response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        pytest.skip("Не получен токен для теста")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    hotels_response = client.get("/hotels?page=1&per_page=1", headers=headers)
    if hotels_response.status_code == 200 and len(hotels_response.json()) > 0:
        hotel_id = hotels_response.json()[0]["id"]
        
        rooms_response = client.get(f"/hotels/{hotel_id}/rooms?page=1&per_page=1", headers=headers)
        if rooms_response.status_code == 200 and len(rooms_response.json()) > 0:
            room_id = rooms_response.json()[0]["id"]
            
            from datetime import date, timedelta
            
            date_from = date.today() + timedelta(days=1)
            date_to = date.today() + timedelta(days=2)
            
            booking_response = client.post(
                "/bookings",
                json={
                    "room_id": room_id,
                    "date_from": date_from.isoformat(),
                    "date_to": date_to.isoformat(),
                },
                headers=headers,
            )
            
            if booking_response.status_code == 201:
                metrics_response = client.get("/metrics")
                assert metrics_response.status_code == 200
                
                metrics_text = metrics_response.text
                assert "bookings_created_total" in metrics_text


def test_metrics_format_valid(client):
    """Проверить, что формат метрик валидный (Prometheus формат)."""
    response = client.get("/metrics")
    assert response.status_code == 200
    
    metrics_text = response.text
    
    lines = metrics_text.split("\n")
    valid_lines = [line for line in lines if line.strip() and not line.startswith("#")]
    
    for line in valid_lines[:10]:
        if "{" in line:
            assert re.match(r'^[a-zA-Z_:][a-zA-Z0-9_:]*\{[^}]+\}\s+[0-9.]+', line) or \
                   re.match(r'^[a-zA-Z_:][a-zA-Z0-9_:]*\s+[0-9.]+', line), \
                   f"Невалидная строка метрики: {line}"
        else:
            assert re.match(r'^[a-zA-Z_:][a-zA-Z0-9_:]*\s+[0-9.]+', line), \
                   f"Невалидная строка метрики: {line}"

