#!/bin/bash
# Скрипт для запуска тестов с покрытием

echo "🔧 Установка PYTHONPATH..."
export PYTHONPATH="$PYTHONPATH:$(pwd):$(pwd)/backend"

echo "🧪 Запуск тестов с проверкой покрытия..."
echo "=========================================="

# Вариант 1: Все тесты с детальным отчетом
echo -e "\n📊 ВАРИАНТ 1: Общее покрытие (сводка)"
pytest --cov=backend backend/tests/ --cov-report=term

echo -e "\n📈 ВАРИАНТ 2: Детальное покрытие (показывает непокрытые строки)"
pytest --cov=backend backend/tests/ --cov-report=term-missing

echo -e "\n📁 ВАРИАНТ 3: Создание HTML отчета"
pytest --cov=backend backend/tests/ --cov-report=html

if [ -d "htmlcov" ] && [ -f "htmlcov/index.html" ]; then
    echo -e "\n✅ HTML отчет создан: htmlcov/index.html"
    echo "   Чтобы открыть: open htmlcov/index.html"
else
    echo -e "\n❌ HTML отчет не создан"
fi

echo -e "\n=========================================="
echo "Краткая справка:"
echo "--cov=backend    : Проверять покрытие модуля backend"
echo "--cov-report=term: Краткий отчет в консоли"
echo "--cov-report=term-missing: Подробный отчет с непокрытыми строками"
echo "--cov-report=html: HTML отчет для браузера"