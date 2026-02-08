#!/bin/bash
# Скрипт для настройки GitLab remote и автоматического push

set -e

echo "🔧 Настройка GitLab remote..."

# Проверяем, что мы в git репозитории
if [ ! -d .git ]; then
    echo "❌ Ошибка: не найден .git каталог. Запустите скрипт из корня проекта."
    exit 1
fi

# Проверяем существующие remotes
echo ""
echo "📋 Текущие remotes:"
git remote -v

# Запрашиваем URL GitLab репозитория
echo ""
read -p "Введите URL GitLab репозитория (например: git@gitlab.com:group/project.git): " GITLAB_URL

if [ -z "$GITLAB_URL" ]; then
    echo "❌ URL не может быть пустым!"
    exit 1
fi

# Проверяем, существует ли уже gitlab remote
if git remote get-url gitlab >/dev/null 2>&1; then
    echo "⚠️  Remote 'gitlab' уже существует."
    read -p "Заменить? (y/n): " REPLACE
    if [ "$REPLACE" = "y" ] || [ "$REPLACE" = "Y" ]; then
        git remote set-url gitlab "$GITLAB_URL"
        echo "✅ Remote 'gitlab' обновлен"
    else
        echo "ℹ️  Remote 'gitlab' не изменен"
    fi
else
    # Добавляем новый remote
    git remote add gitlab "$GITLAB_URL"
    echo "✅ Remote 'gitlab' добавлен"
fi

# Настраиваем автоматический push в оба репозитория через origin
echo ""
read -p "Настроить автоматический push в оба репозитория через 'git push origin'? (y/n): " SETUP_AUTO

if [ "$SETUP_AUTO" = "y" ] || [ "$SETUP_AUTO" = "Y" ]; then
    # Получаем текущий URL origin
    ORIGIN_URL=$(git remote get-url origin)
    
    # Добавляем GitLab как дополнительный push URL для origin
    git remote set-url --add --push origin "$ORIGIN_URL"
    git remote set-url --add --push origin "$GITLAB_URL"
    
    echo "✅ Настроен автоматический push: 'git push origin' теперь пушит в оба репозитория"
else
    echo "ℹ️  Автоматический push не настроен. Используйте 'git push origin && git push gitlab'"
fi

# Создаем hooks для автоматического push
echo ""
echo "📝 Создание git hooks..."

# Post-commit hook
cat > .git/hooks/post-commit << 'HOOK_EOF'
#!/bin/bash
# Автоматический push в оба репозитория после коммита (опционально)
# Раскомментируйте строки ниже, если хотите автоматический push после каждого коммита

# git push origin HEAD 2>/dev/null || true
# git push gitlab HEAD 2>/dev/null || true
HOOK_EOF

# Post-merge hook
cat > .git/hooks/post-merge << 'HOOK_EOF'
#!/bin/bash
# Автоматический push в оба репозитория после merge (опционально)
# Раскомментируйте строки ниже, если хотите автоматический push после каждого merge

# git push origin HEAD 2>/dev/null || true
# git push gitlab HEAD 2>/dev/null || true
HOOK_EOF

chmod +x .git/hooks/post-commit
chmod +x .git/hooks/post-merge

echo "✅ Git hooks созданы (по умолчанию отключены, раскомментируйте в файлах для включения)"

# Проверяем подключение
echo ""
echo "🔍 Проверка подключения к GitLab..."
if git ls-remote gitlab >/dev/null 2>&1; then
    echo "✅ Подключение к GitLab успешно!"
else
    echo "⚠️  Не удалось подключиться к GitLab. Проверьте:"
    echo "   - Правильность URL"
    echo "   - Настройку SSH ключей"
    echo "   - Права доступа к репозиторию"
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
    echo "   git push origin && git push gitlab  # Пушит в оба"
fi

