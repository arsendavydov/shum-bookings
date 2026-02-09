#!/bin/bash
# Скрипт для настройки GitLab через Personal Access Token

set -e

GITLAB_REPO="shum-bookin/shum-booking"
GITLAB_URL="https://gitlab.com/${GITLAB_REPO}.git"

echo "🔐 Настройка GitLab через Personal Access Token"
echo ""

# Проверяем, что мы в git репозитории
if [ ! -d .git ]; then
    echo "❌ Ошибка: не найден .git каталог"
    exit 1
fi

# Показываем текущие remotes
echo "📋 Текущие remotes:"
git remote -v
echo ""

# Запрашиваем токен
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Создайте Personal Access Token в GitLab:"
echo "   https://gitlab.com/-/user_settings/personal_access_tokens"
echo ""
echo "   Нужные права: api, read_repository, write_repository"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -sp "Введите ваш Personal Access Token (glpat-...): " GITLAB_TOKEN
echo ""

if [ -z "$GITLAB_TOKEN" ]; then
    echo "❌ Токен не может быть пустым!"
    exit 1
fi

# Проверяем формат токена
if [[ ! "$GITLAB_TOKEN" =~ ^glpat- ]]; then
    echo "⚠️  Предупреждение: токен должен начинаться с 'glpat-'"
    read -p "Продолжить? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        exit 1
    fi
fi

# Проверяем, существует ли уже gitlab remote
if git remote get-url gitlab >/dev/null 2>&1; then
    echo "⚠️  Remote 'gitlab' уже существует: $(git remote get-url gitlab)"
    read -p "Заменить? (y/n): " REPLACE
    if [ "$REPLACE" = "y" ] || [ "$REPLACE" = "Y" ]; then
        git remote set-url gitlab "https://oauth2:${GITLAB_TOKEN}@gitlab.com/${GITLAB_REPO}.git"
        echo "✅ Remote 'gitlab' обновлен"
    else
        GITLAB_EXISTING=$(git remote get-url gitlab)
        if [[ "$GITLAB_EXISTING" == *"oauth2"* ]]; then
            # Обновляем токен в существующем URL
            git remote set-url gitlab "https://oauth2:${GITLAB_TOKEN}@gitlab.com/${GITLAB_REPO}.git"
            echo "✅ Токен обновлен в существующем remote"
        else
            echo "ℹ️  Используется существующий remote без изменений"
        fi
    fi
else
    git remote add gitlab "https://oauth2:${GITLAB_TOKEN}@gitlab.com/${GITLAB_REPO}.git"
    echo "✅ Remote 'gitlab' добавлен"
fi

# Настраиваем автоматический push в оба репозитория
echo ""
read -p "Настроить автоматический push в оба репозитория при 'git push origin'? (y/n): " SETUP_AUTO

if [ "$SETUP_AUTO" = "y" ] || [ "$SETUP_AUTO" = "Y" ]; then
    ORIGIN_URL=$(git remote get-url origin)
    
    # Проверяем, настроен ли уже push в оба
    PUSH_URLS=$(git remote get-url --push --all origin 2>/dev/null || echo "")
    
    if echo "$PUSH_URLS" | grep -q "gitlab.com"; then
        echo "ℹ️  Автоматический push уже настроен"
    else
        git remote set-url --add --push origin "$ORIGIN_URL"
        git remote set-url --add --push origin "https://oauth2:${GITLAB_TOKEN}@gitlab.com/${GITLAB_REPO}.git"
        echo "✅ Настроен автоматический push!"
        echo "   Теперь 'git push origin' будет пушить в оба репозитория"
    fi
else
    echo "ℹ️  Автоматический push не настроен"
    echo "   Используйте: git push origin && git push gitlab"
fi

# Проверяем подключение
echo ""
echo "🔍 Проверка подключения к GitLab..."
if git ls-remote gitlab >/dev/null 2>&1; then
    echo "✅ Подключение к GitLab успешно!"
else
    echo "⚠️  Не удалось подключиться. Проверьте:"
    echo "   - Правильность токена"
    echo "   - Права доступа токена (read_repository, write_repository)"
    echo "   - Доступ к репозиторию"
fi

# Итоговая информация
echo ""
echo "📋 Итоговая конфигурация:"
git remote -v

echo ""
echo "✅ Настройка завершена!"
echo ""
echo "💡 Использование:"
if [ "$SETUP_AUTO" = "y" ] || [ "$SETUP_AUTO" = "Y" ]; then
    echo "   git push origin    # Пушит в оба репозитория (GitHub + GitLab)"
else
    echo "   git push origin    # Пушит в GitHub"
    echo "   git push gitlab    # Пушит в GitLab"
fi

echo ""
echo "📤 Первый push в GitLab:"
echo "   git push gitlab main    # Push текущей ветки"
echo "   git push gitlab --all   # Push всех веток"

echo ""
echo "⚠️  ВАЖНО: Токен сохранен в .git/config"
echo "   Для безопасности используйте git credential helper или переменные окружения"

