"""add database indexes

Revision ID: add_db_indexes
Revises: add_images_tables
Create Date: 2026-02-05 22:19:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_db_indexes'
down_revision: Union[str, None] = 'add_images_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Индекс на users.email для быстрого поиска пользователей по email
    # Примечание: unique constraint уже создает индекс автоматически в PostgreSQL,
    # но явно создаем для ясности и единообразия
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Индекс на hotels.city_id для фильтрации отелей по городу
    op.create_index('ix_hotels_city_id', 'hotels', ['city_id'], unique=False)
    
    # Индекс на rooms.hotel_id для поиска номеров по отелю
    op.create_index('ix_rooms_hotel_id', 'rooms', ['hotel_id'], unique=False)
    
    # Индексы на bookings для проверки доступности номеров
    # room_id используется в WHERE вместе с date_from и date_to
    op.create_index('ix_bookings_room_id', 'bookings', ['room_id'], unique=False)
    op.create_index('ix_bookings_date_from', 'bookings', ['date_from'], unique=False)
    op.create_index('ix_bookings_date_to', 'bookings', ['date_to'], unique=False)
    
    # Составной индекс на (room_id, date_from, date_to) для оптимизации запросов проверки конфликтов
    # Это улучшит производительность запросов вида:
    # WHERE room_id = X AND date_from < Y AND date_to > Z
    op.create_index('ix_bookings_room_dates', 'bookings', ['room_id', 'date_from', 'date_to'], unique=False)
    
    # Индекс на bookings.user_id для поиска бронирований пользователя
    op.create_index('ix_bookings_user_id', 'bookings', ['user_id'], unique=False)
    
    # Индекс на cities.country_id для связи с страной
    op.create_index('ix_cities_country_id', 'cities', ['country_id'], unique=False)


def downgrade() -> None:
    # Удаляем индексы в обратном порядке
    op.drop_index('ix_cities_country_id', table_name='cities')
    op.drop_index('ix_bookings_user_id', table_name='bookings')
    op.drop_index('ix_bookings_room_dates', table_name='bookings')
    op.drop_index('ix_bookings_date_to', table_name='bookings')
    op.drop_index('ix_bookings_date_from', table_name='bookings')
    op.drop_index('ix_bookings_room_id', table_name='bookings')
    op.drop_index('ix_rooms_hotel_id', table_name='rooms')
    op.drop_index('ix_hotels_city_id', table_name='hotels')
    op.drop_index('ix_users_email', table_name='users')

