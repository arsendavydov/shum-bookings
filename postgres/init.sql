-- Создание базы данных booking
CREATE DATABASE booking;

-- Создание тестовой базы данных test
CREATE DATABASE test;

-- Примечание: После создания базы данных booking, 
-- для работы с ней нужно подключаться напрямую к ней:
-- psql -h localhost -U postgres -d booking
--
-- Можно добавить дополнительные настройки или таблицы здесь
-- Например, создание расширений (выполняется при подключении к booking):
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

