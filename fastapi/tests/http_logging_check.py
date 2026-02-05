"""
Небольшой утилитарный скрипт для ручной проверки HTTP‑логирования.

Что делает:
1. Делает запрос без авторизации:        GET /hotels
2. Регистрирует и логинит пользователя,  GET /bookings с авторизацией
3. Проверяет, что эти запросы видны:
   - в docker‑логах контейнера fastapi_app
   - в файле fastapi/logs/app.log

Запускать из директории fastapi:
    python tests/http_logging_check.py
"""

import subprocess
import time
from pathlib import Path

import httpx

BASE_URL = "http://localhost:8000"
CONTAINER_NAME = "fastapi_app"

ROOT_DIR = Path(__file__).resolve().parents[1]  # .../fastapi
APP_LOG_PATH = ROOT_DIR / "logs" / "app.log"

# Тестовый пользователь для проверки авторизации
TEST_EMAIL_DOMAIN = "example.com"
TEST_PASSWORD = "test_http_logging_123"


def run_docker_logs(tail: int = 400) -> str:
    """Считать хвост логов из контейнера fastapi_app."""
    try:
        result = subprocess.run(
            ["docker", "logs", CONTAINER_NAME, "--tail", str(tail)],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except Exception as exc:
        print(f"[ERROR] Не удалось прочитать docker logs {CONTAINER_NAME}: {exc}")
        return ""

    if result.returncode != 0:
        print(f"[ERROR] docker logs вернул код {result.returncode}: {result.stderr.strip()}")
        return ""

    return result.stdout


def main() -> int:
    print(f"[INFO] BASE_URL = {BASE_URL}")
    print(f"[INFO] APP_LOG_PATH = {APP_LOG_PATH}")

    if not APP_LOG_PATH.exists():
        print(f"[WARN] Файл лога {APP_LOG_PATH} пока не существует. Продолжаю, он может появиться после запросов.")
        before_log = ""
    else:
        before_log = APP_LOG_PATH.read_text(encoding="utf-8", errors="ignore")

    before_len = len(before_log)

    # --- HTTP запросы ---
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Неавторизованный запрос к отелям
        print("[STEP] GET /hotels (без авторизации)")
        hotels_resp = client.get(
            "/hotels",
            params={"sort_by": "id", "order": "asc", "page": 1, "per_page": 10},
        )
        print(f"[INFO] /hotels status = {hotels_resp.status_code}")

        # 2. Регистрация и логин пользователя
        ts = int(time.time() * 1000)
        test_email = f"http-logging-{ts}@{TEST_EMAIL_DOMAIN}"
        print(f"[STEP] POST /auth/register email={test_email}")
        reg_resp = client.post("/auth/register", json={"email": test_email, "password": TEST_PASSWORD})
        print(f"[INFO] /auth/register status = {reg_resp.status_code}")

        print("[STEP] POST /auth/login")
        login_resp = client.post("/auth/login", json={"email": test_email, "password": TEST_PASSWORD})
        print(f"[INFO] /auth/login status = {login_resp.status_code}")

        access_token: str | None = None
        if login_resp.status_code == 200:
            data = login_resp.json()
            access_token = data.get("access_token")

        # 3. Авторизованный запрос к бронированиям
        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
            print("[STEP] GET /bookings (с авторизацией)")
            bookings_resp = client.get("/bookings", params={"page": 1, "per_page": 10}, headers=headers)
            print(f"[INFO] /bookings status = {bookings_resp.status_code}")
        else:
            print("[WARN] Не удалось получить access_token, GET /bookings пропускаю")

    # Немного даём времени логгеру записать в файл
    time.sleep(0.5)

    # --- Проверка файлового лога ---
    if APP_LOG_PATH.exists():
        after_log = APP_LOG_PATH.read_text(encoding="utf-8", errors="ignore")
        new_part = after_log[before_len:]
    else:
        print(f"[ERROR] Файл {APP_LOG_PATH} не создан после запросов")
        new_part = ""

    print("\n[CHECK] Поиск записей в app.log:")
    has_hotels_file = "GET /hotels" in new_part
    has_bookings_file = "GET /bookings" in new_part
    print(f"  - GET /hotels в app.log:   {'OK' if has_hotels_file else 'NO'}")
    print(f"  - GET /bookings в app.log: {'OK' if has_bookings_file else 'NO'}")

    # --- Проверка логов контейнера ---
    print("\n[CHECK] Поиск записей в docker logs fastapi_app:")
    container_logs = run_docker_logs()
    has_hotels_docker = "GET /hotels" in container_logs
    has_bookings_docker = "GET /bookings" in container_logs
    print(f"  - GET /hotels в docker logs:   {'OK' if has_hotels_docker else 'NO'}")
    print(f"  - GET /bookings в docker logs: {'OK' if has_bookings_docker else 'NO'}")

    all_ok = (
        has_hotels_file
        and has_hotels_docker
        and (has_bookings_file or not access_token)
        and (has_bookings_docker or not access_token)
    )

    if all_ok:
        print("\n[RESULT] HTTP‑логи корректно пишутся и в файл, и в логи контейнера.")
        return 0

    print("\n[RESULT] Не все ожидаемые записи найдены. См. вывод выше.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
