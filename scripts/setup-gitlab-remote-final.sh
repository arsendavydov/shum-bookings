#!/bin/bash
# Финальная настройка GitLab remote для push в оба репозитория

set -e

GITLAB_URL="git@gitlab.com:shum-bookin/shum-booking.git"

echo "🔧 Настройка GitLab remote..."
echo ""

# Проверяем подключение к GitLab
echo "🔍 Проверка SSH подключения к GitLab..."
if ssh -T git@gitlab.com 2>&1 | grep -q "Welcome to GitLab"; then
    echo "✅ Подключение к GitLab успешно!"
else
    echo "⚠️  SSH ключ еще не добавлен в GitLab или подключение не установлено"
    echo "   Добавьте ключ здесь: https://gitlab.com/-/profile/keys"
    echo "   Публичный ключ:"
    cat ~/.ssh/id_ed25519_gitlab.pub
    echo ""
    read -p "Нажмите Enter после добавления ключа в GitLab..."
    
    # Повторная проверка
    if ssh -T git@gitlab.com 2>&1 | grep -q "Welcome to GitLab"; then
        echo "✅ Подключение установлено!"
    else
        echo "❌ Подключение не установлено. Проверьте ключ в GitLab."
        exit 1
    fi
fi

echo ""
echo "📋 Текущие remotes:"
git remote -v

echo ""
# Проверяем, существует ли уже gitlab remote
if git remote get-url gitlab >/dev/null 2>&1; then
    echo "⚠️  Remote 'gitlab' уже существует: $(git remote get-url gitlab)"
    read -p "Заменить на $GITLAB_URL? (y/n): " REPLACE
    if [ "$REPLACE" = "y" ] || [ "$REPLACE" = "Y" ]; then
        git remote set-url gitlab "$GITLAB_URL"
        echo "✅ Remote 'gitlab' обновлен"
    else
        GITLAB_URL=$(git remote get-url gitlab)
        echo "ℹ️  Используется существующий remote: $GITLAB_URL"
    fi
else
    git remote add gitlab "$GITLAB_URL"
    echo "✅ Remote 'gitlab' добавлен"
fi

echo ""
echo "🔧 Настройка автоматического push в оба репозитория..."
ORIGIN_URL=$(git remote get-url origin)

# Проверяем, настроен ли уже push в оба
if git remote get-url --push --all origin | grep -q "gitlab.com"; then
    echo "ℹ️  Автоматический push уже настроен"
else
    git remote set-url --add --push origin "$ORIGIN_URL"
    git remote set-url --add --push origin "$GITLAB_URL"
    echo "✅ Настроен автоматический push!"
fi

echo ""
echo "📋 Итоговая конфигурация:"
git remote -v

echo ""
echo "✅ Готово!"
echo ""
echo "💡 Теперь используйте:"
echo "   git push origin    # Пушит сразу в GitHub и GitLab!"
echo ""
echo "📤 Первый push в GitLab:"
echo "   git push gitlab main    # Push текущей ветки"
echo "   git push gitlab --all   # Push всех веток"

