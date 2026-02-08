#!/bin/bash
# Простой скрипт для добавления GitLab remote

set -e

echo "🔧 Добавление GitLab remote..."

# Проверяем, что мы в git репозитории
if [ ! -d .git ]; then
    echo "❌ Ошибка: не найден .git каталог"
    exit 1
fi

# Проверяем существующие remotes
echo ""
echo "📋 Текущие remotes:"
git remote -v

# Запрашиваем URL GitLab
echo ""
read -p "Введите URL GitLab репозитория (git@gitlab.com:group/project.git или https://...): " GITLAB_URL

if [ -z "$GITLAB_URL" ]; then
    echo "❌ URL не может быть пустым!"
    exit 1
fi

# Проверяем, существует ли уже gitlab remote
if git remote get-url gitlab >/dev/null 2>&1; then
    echo "⚠️  Remote 'gitlab' уже существует: $(git remote get-url gitlab)"
    read -p "Заменить на новый URL? (y/n): " REPLACE
    if [ "$REPLACE" = "y" ] || [ "$REPLACE" = "Y" ]; then
        git remote set-url gitlab "$GITLAB_URL"
        echo "✅ Remote 'gitlab' обновлен"
    else
        echo "ℹ️  Remote 'gitlab' не изменен"
        exit 0
    fi
else
    git remote add gitlab "$GITLAB_URL"
    echo "✅ Remote 'gitlab' добавлен"
fi

# Настраиваем автоматический push в оба репозитория
echo ""
read -p "Настроить автоматический push в оба репозитория при 'git push origin'? (y/n): " SETUP_AUTO

if [ "$SETUP_AUTO" = "y" ] || [ "$SETUP_AUTO" = "Y" ]; then
    # Получаем текущий URL origin
    ORIGIN_URL=$(git remote get-url origin)
    
    # Настраиваем origin для push в оба репозитория
    git remote set-url --add --push origin "$ORIGIN_URL"
    git remote set-url --add --push origin "$GITLAB_URL"
    
    echo "✅ Настроен автоматический push!"
    echo "   Теперь 'git push origin' будет пушить в оба репозитория"
else
    echo "ℹ️  Автоматический push не настроен"
    echo "   Используйте: git push origin && git push gitlab"
fi

# Проверяем подключение
echo ""
echo "🔍 Проверка подключения..."
if git ls-remote gitlab >/dev/null 2>&1; then
    echo "✅ Подключение к GitLab успешно!"
else
    echo "⚠️  Не удалось подключиться. Проверьте URL и SSH ключи"
fi

echo ""
echo "📋 Итоговая конфигурация:"
git remote -v

echo ""
echo "✅ Готово!"

