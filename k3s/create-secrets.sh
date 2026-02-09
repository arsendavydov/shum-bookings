#!/bin/bash

# ============================================================================
# Скрипт для создания K3s ConfigMap и Secrets из .prod.env
# ============================================================================
# Использование: ./create-secrets.sh
# 
# Требования:
# - kubectl установлен и настроен
# - .prod.env файл существует в корне проекта
# - namespace "booking" создан
#
# Скрипт создает:
# - ConfigMap "booking-config" с несекретными переменными из .prod.env
# - Secret "booking-secrets" с секретными переменными из .prod.env

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.prod.env"
NAMESPACE="booking"

echo "🔐 Создание K3s ConfigMap и Secrets из .prod.env..."
echo ""

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
# Используем set -a для автоматического экспорта всех переменных
set -a
source "$ENV_FILE"
set +a

# Проверка обязательных секретных переменных
if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "CHANGE_ME" ]; then
    echo "❌ DB_PASSWORD не установлен или имеет значение по умолчанию"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "CHANGE_ME_GENERATE_NEW_SECRET_KEY" ]; then
    echo "❌ JWT_SECRET_KEY не установлен или имеет значение по умолчанию"
    exit 1
fi

# ============================================================================
# Создание ConfigMap с несекретными переменными
# ============================================================================
echo "📋 Создание ConfigMap booking-config..."

# Удаление существующего ConfigMap (если есть)
if kubectl get configmap booking-config -n "$NAMESPACE" &> /dev/null; then
    echo "🗑️  Удаление существующего ConfigMap..."
    kubectl delete configmap booking-config -n "$NAMESPACE"
fi

# Создание ConfigMap с несекретными переменными из .prod.env
kubectl create configmap booking-config \
    --from-literal=DB_HOST="${DB_HOST:-postgres-service}" \
    --from-literal=DB_PORT="${DB_PORT:-5432}" \
    --from-literal=DB_NAME="${DB_NAME:-booking}" \
    --from-literal=REDIS_HOST="${REDIS_HOST:-redis-service}" \
    --from-literal=REDIS_PORT="${REDIS_PORT:-6379}" \
    --from-literal=REDIS_DB="${REDIS_DB:-0}" \
    --from-literal=JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}" \
    --from-literal=JWT_ACCESS_TOKEN_EXPIRE_MINUTES="${JWT_ACCESS_TOKEN_EXPIRE_MINUTES:-30}" \
    --from-literal=JWT_REFRESH_TOKEN_EXPIRE_DAYS="${JWT_REFRESH_TOKEN_EXPIRE_DAYS:-30}" \
    --from-literal=JWT_COOKIE_SECURE="${JWT_COOKIE_SECURE:-true}" \
    --from-literal=LOG_LEVEL="${LOG_LEVEL:-INFO}" \
    --from-literal=LOG_FORMAT_JSON="${LOG_FORMAT_JSON:-true}" \
    --from-literal=MAX_IMAGE_FILE_SIZE_MB="${MAX_IMAGE_FILE_SIZE_MB:-10}" \
    --from-literal=RATE_LIMIT_ENABLED="${RATE_LIMIT_ENABLED:-true}" \
    --from-literal=RATE_LIMIT_PER_MINUTE="${RATE_LIMIT_PER_MINUTE:-60}" \
    --from-literal=RATE_LIMIT_AUTH_PER_MINUTE="${RATE_LIMIT_AUTH_PER_MINUTE:-5}" \
    --from-literal=PYTHONUNBUFFERED="${PYTHONUNBUFFERED:-1}" \
    --from-literal=PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}" \
    --from-literal=ROOT_PATH="${ROOT_PATH:-}" \
    --namespace="$NAMESPACE"

echo "✅ ConfigMap booking-config успешно создан"
echo ""

# ============================================================================
# Создание Secret с секретными переменными
# ============================================================================
echo "🔑 Создание Secret booking-secrets..."

# Удаление существующего secret (если есть)
if kubectl get secret booking-secrets -n "$NAMESPACE" &> /dev/null; then
    echo "🗑️  Удаление существующего secret..."
    kubectl delete secret booking-secrets -n "$NAMESPACE"
fi

# Создание Secret с секретными переменными из .prod.env
kubectl create secret generic booking-secrets \
    --from-literal=DB_USERNAME="${DB_USERNAME:-postgres}" \
    --from-literal=DB_PASSWORD="$DB_PASSWORD" \
    --from-literal=JWT_SECRET_KEY="$JWT_SECRET_KEY" \
    --from-literal=REDIS_PASSWORD="${REDIS_PASSWORD:-}" \
    --namespace="$NAMESPACE"

echo "✅ Secret booking-secrets успешно создан"
echo ""

# ============================================================================
# Проверка результатов
# ============================================================================
echo "📋 Проверка созданных ресурсов:"
echo ""
echo "ConfigMap:"
kubectl get configmap booking-config -n "$NAMESPACE"
echo ""
echo "Secret:"
kubectl get secret booking-secrets -n "$NAMESPACE"
echo ""
echo "💡 Для просмотра значений ConfigMap:"
echo "   kubectl get configmap booking-config -n $NAMESPACE -o yaml"
echo ""
echo "💡 Для просмотра значений Secret (base64):"
echo "   kubectl get secret booking-secrets -n $NAMESPACE -o yaml"

