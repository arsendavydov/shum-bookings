#!/bin/bash
# Скрипт для установки K3s на сервер

set -e

echo "🚀 Установка K3s (легковесный Kubernetes)"
echo ""

# Проверка, что мы на Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Внимание: K3s работает только на Linux"
    echo "   Этот скрипт должен запускаться на сервере с Linux"
    exit 1
fi

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт должен запускаться с правами root (sudo)"
    exit 1
fi

echo "📋 Проверка системы..."
echo ""

# Проверка дистрибутива
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "   OS: $PRETTY_NAME"
else
    echo "   OS: Неизвестный Linux дистрибутив"
fi

# Проверка ресурсов
echo ""
echo "💻 Ресурсы сервера:"
CPU_COUNT=$(nproc)
RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
DISK_GB=$(df -h / | awk 'NR==2 {print $4}')

echo "   CPU: $CPU_COUNT ядер"
echo "   RAM: $RAM_GB GB"
echo "   Disk: $DISK_GB свободно"

# Проверка минимальных требований
if [ "$CPU_COUNT" -lt 2 ]; then
    echo "⚠️  Предупреждение: Рекомендуется минимум 2 ядра CPU"
fi

if [ "$RAM_GB" -lt 2 ]; then
    echo "⚠️  Предупреждение: Рекомендуется минимум 2 GB RAM"
    read -p "Продолжить установку? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        exit 1
    fi
fi

echo ""
read -p "Продолжить установку K3s? (y/n): " INSTALL
if [ "$INSTALL" != "y" ] && [ "$INSTALL" != "Y" ]; then
    echo "Установка отменена"
    exit 0
fi

echo ""
echo "📦 Установка K3s..."
echo ""

# Установка K3s
curl -sfL https://get.k3s.io | sh -

echo ""
echo "✅ K3s установлен!"
echo ""

# Проверка статуса
echo "🔍 Проверка статуса..."
systemctl status k3s --no-pager | head -10

echo ""
echo "📋 Настройка доступа..."
echo ""

# Создать директорию для kubeconfig
KUBE_DIR="$HOME/.kube"
if [ "$SUDO_USER" ]; then
    KUBE_DIR="/home/$SUDO_USER/.kube"
fi

mkdir -p "$KUBE_DIR"

# Скопировать kubeconfig
cp /etc/rancher/k3s/k3s.yaml "$KUBE_DIR/config"
chmod 600 "$KUBE_DIR/config"

if [ "$SUDO_USER" ]; then
    chown -R "$SUDO_USER:$SUDO_USER" "$KUBE_DIR"
fi

echo "✅ Kubeconfig скопирован в $KUBE_DIR/config"
echo ""

# Проверка подключения
echo "🔍 Проверка подключения к кластеру..."
if command -v kubectl >/dev/null 2>&1; then
    export KUBECONFIG="$KUBE_DIR/config"
    kubectl get nodes
    echo ""
    echo "✅ K3s успешно установлен и настроен!"
else
    echo "⚠️  kubectl не найден в PATH"
    echo "   Используйте: export KUBECONFIG=$KUBE_DIR/config"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Следующие шаги:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Проверить установку:"
echo "   kubectl get nodes"
echo ""
echo "2. Получить kubeconfig для GitLab CI/CD:"
echo "   cat $KUBE_DIR/config | base64 -w 0  # Linux"
echo "   cat $KUBE_DIR/config | base64        # macOS"
echo ""
echo "3. Добавить KUBECONFIG в GitLab CI/CD Variables"
echo ""
echo "4. Применить манифесты:"
echo "   kubectl apply -f k8s/namespace.yaml"
echo "   kubectl apply -f k8s/configmap.yaml"
echo "   # ... и так далее"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

