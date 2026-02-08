#!/bin/bash

# ============================================================================
# Скрипт для создания K3s secrets из .prod.env
# ============================================================================
# Использование: ./create-secrets.sh
# 
# Требования:
# - kubectl установлен и настроен
# - .prod.env файл существует в корне проекта
# - namespace "booking" создан

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.prod.env"
NAMESPACE="booking"

echo "🔐 Создание K3s secrets из .prod.env..."

# Проверка наличия .prod.env
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Файл .prod.env не найден в $PROJECT_ROOT"
    exit 1
fi

# Проверка наличия kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl не установлен"
    exit 1
fi

# Проверка подключения к кластеру
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Не удается подключиться к K3s кластеру"
    exit 1
fi

# Создание namespace, если не существует
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "📦 Создание namespace $NAMESPACE..."
    kubectl create namespace "$NAMESPACE"
fi

# Загрузка переменных из .prod.env
source "$ENV_FILE"

# Проверка обязательных переменных
if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "CHANGE_ME" ]; then
    echo "❌ DB_PASSWORD не установлен или имеет значение по умолчанию"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "CHANGE_ME_GENERATE_NEW_SECRET_KEY" ]; then
    echo "❌ JWT_SECRET_KEY не установлен или имеет значение по умолчанию"
    exit 1
fi

# Удаление существующего secret (если есть)
if kubectl get secret booking-secrets -n "$NAMESPACE" &> /dev/null; then
    echo "🗑️  Удаление существующего secret..."
    kubectl delete secret booking-secrets -n "$NAMESPACE"
fi

# Создание нового secret
echo "🔑 Создание secret booking-secrets..."

kubectl create secret generic booking-secrets \
    --from-literal=DB_USERNAME="${DB_USERNAME:-postgres}" \
    --from-literal=DB_PASSWORD="$DB_PASSWORD" \
    --from-literal=JWT_SECRET_KEY="$JWT_SECRET_KEY" \
    --from-literal=REDIS_PASSWORD="${REDIS_PASSWORD:-}" \
    --namespace="$NAMESPACE"

echo "✅ Secret booking-secrets успешно создан в namespace $NAMESPACE"
echo ""
echo "📋 Проверка secret:"
kubectl get secret booking-secrets -n "$NAMESPACE"

echo ""
echo "💡 Для просмотра значений (base64):"
echo "   kubectl get secret booking-secrets -n $NAMESPACE -o yaml"

