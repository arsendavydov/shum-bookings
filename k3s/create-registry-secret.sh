#!/bin/bash

# ============================================================================
# Скрипт для создания K3s secret для доступа к GitLab Container Registry
# ============================================================================
# Использование: ./create-registry-secret.sh
# 
# Требования:
# - kubectl установлен и настроен
# - GitLab Personal Access Token или Deploy Token с правами read_registry
# - namespace "booking" создан
#
# Переменные окружения:
# - GITLAB_REGISTRY_USER - имя пользователя GitLab или deploy token username
# - GITLAB_REGISTRY_PASSWORD - Personal Access Token или deploy token password
# - GITLAB_REGISTRY_URL - URL реестра (по умолчанию: registry.gitlab.com)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.prod.env"
NAMESPACE="booking"
SECRET_NAME="gitlab-registry-secret"
REGISTRY_URL="${GITLAB_REGISTRY_URL:-registry.gitlab.com}"

echo "🔐 Создание K3s secret для доступа к GitLab Container Registry..."
echo ""

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

# Загрузка переменных из .prod.env (если файл существует)
if [ -f "$ENV_FILE" ]; then
    echo "📋 Загрузка переменных из .prod.env..."
    source "$ENV_FILE"
fi

# Запрос credentials, если не заданы в переменных окружения
if [ -z "$GITLAB_REGISTRY_USER" ]; then
    echo "Введите имя пользователя GitLab или deploy token username:"
    read -r GITLAB_REGISTRY_USER
fi

if [ -z "$GITLAB_REGISTRY_PASSWORD" ]; then
    echo "Введите Personal Access Token или deploy token password:"
    read -rs GITLAB_REGISTRY_PASSWORD
    echo ""
fi

if [ -z "$GITLAB_REGISTRY_USER" ] || [ -z "$GITLAB_REGISTRY_PASSWORD" ]; then
    echo "❌ GITLAB_REGISTRY_USER и GITLAB_REGISTRY_PASSWORD обязательны!"
    exit 1
fi

# Удаление существующего secret (если есть)
if kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" &> /dev/null; then
    echo "🗑️  Удаление существующего secret..."
    kubectl delete secret "$SECRET_NAME" -n "$NAMESPACE"
fi

# Создание нового secret для Docker registry
echo "🔑 Создание secret $SECRET_NAME..."
kubectl create secret docker-registry "$SECRET_NAME" \
    --docker-server="$REGISTRY_URL" \
    --docker-username="$GITLAB_REGISTRY_USER" \
    --docker-password="$GITLAB_REGISTRY_PASSWORD" \
    --namespace="$NAMESPACE"

echo ""
echo "✅ Secret $SECRET_NAME успешно создан в namespace $NAMESPACE"
echo ""
echo "📋 Проверка secret:"
kubectl get secret "$SECRET_NAME" -n "$NAMESPACE"

echo ""
echo "💡 Теперь нужно добавить imagePullSecrets в deployment манифесты:"
echo "   imagePullSecrets:"
echo "   - name: $SECRET_NAME"
echo ""
echo "   Или применить обновленные манифесты из k3s/"

