#!/bin/bash
# Скрипт для парсинга JSON логов из Docker контейнеров
# Использование: ./parse-docker-logs.sh <container_name>

CONTAINER_NAME=${1:-"fastapi_app"}

if [ -z "$CONTAINER_NAME" ]; then
    echo "Использование: $0 <container_name>"
    echo "Пример: $0 fastapi_app"
    exit 1
fi

# Проверяем, что контейнер существует
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Контейнер ${CONTAINER_NAME} не найден"
    exit 1
fi

echo "📋 Логи контейнера ${CONTAINER_NAME}:"
echo "=================================="
echo ""

# Получаем логи и пытаемся распарсить JSON
docker logs "${CONTAINER_NAME}" 2>&1 | while IFS= read -r line; do
    # Проверяем, является ли строка валидным JSON
    if echo "$line" | jq . >/dev/null 2>&1; then
        # Красиво форматируем JSON
        echo "$line" | jq .
    else
        # Если не JSON, выводим как есть
        echo "$line"
    fi
done

