#!/bin/bash

# Скрипт для запуска тестов
# Использование: ./run_tests.sh

# Запускаем pytest
python3.11 -m pytest tests/ -v
