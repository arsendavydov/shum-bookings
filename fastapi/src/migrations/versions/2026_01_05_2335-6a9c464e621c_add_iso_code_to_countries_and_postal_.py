"""add_iso_code_to_countries_and_postal_code_to_hotels

Revision ID: 6a9c464e621c
Revises: 1cbcec213216
Create Date: 2026-01-05 23:35:16.675864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a9c464e621c'
down_revision: Union[str, Sequence[str], None] = '1cbcec213216'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем колонку iso_code как nullable
    op.add_column('countries', sa.Column('iso_code', sa.String(length=2), nullable=True))
    
    # Заполняем ISO коды для существующих стран
    connection = op.get_bind()
    iso_codes = {
        'Россия': 'RU',
        'ОАЭ': 'AE',
        'Франция': 'FR',
        'Великобритания': 'GB',
        'Италия': 'IT',
        'Таиланд': 'TH',
        'Гонконг': 'HK',
        'США': 'US',
        'Япония': 'JP'
    }
    
    for country_name, iso_code in iso_codes.items():
        connection.execute(
            sa.text("UPDATE countries SET iso_code = :iso_code WHERE name = :name"),
            {"iso_code": iso_code, "name": country_name}
        )
    
    # Делаем колонку NOT NULL
    op.alter_column('countries', 'iso_code', nullable=False)
    
    # Создаем unique constraint на iso_code
    op.create_unique_constraint('countries_iso_code_key', 'countries', ['iso_code'])
    
    # Добавляем колонку postal_code в hotels
    op.add_column('hotels', sa.Column('postal_code', sa.String(length=20), nullable=True))
    
    # Исправляем foreign keys для bookings (добавляем CASCADE)
    op.drop_constraint('bookings_user_id_fkey', 'bookings', type_='foreignkey')
    op.drop_constraint('bookings_room_id_fkey', 'bookings', type_='foreignkey')
    op.create_foreign_key('bookings_user_id_fkey', 'bookings', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('bookings_room_id_fkey', 'bookings', 'rooms', ['room_id'], ['id'], ondelete='CASCADE')
    
    # Исправляем foreign key для rooms (добавляем CASCADE)
    op.drop_constraint('rooms_hotel_id_fkey', 'rooms', type_='foreignkey')
    op.create_foreign_key('rooms_hotel_id_fkey', 'rooms', 'hotels', ['hotel_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    # Восстанавливаем foreign keys для rooms
    op.drop_constraint('rooms_hotel_id_fkey', 'rooms', type_='foreignkey')
    op.create_foreign_key('rooms_hotel_id_fkey', 'rooms', 'hotels', ['hotel_id'], ['id'], ondelete='CASCADE')
    
    # Восстанавливаем foreign keys для bookings
    op.drop_constraint('bookings_user_id_fkey', 'bookings', type_='foreignkey')
    op.drop_constraint('bookings_room_id_fkey', 'bookings', type_='foreignkey')
    op.create_foreign_key('bookings_user_id_fkey', 'bookings', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('bookings_room_id_fkey', 'bookings', 'rooms', ['room_id'], ['id'], ondelete='CASCADE')
    
    # Удаляем колонку postal_code
    op.drop_column('hotels', 'postal_code')
    
    # Удаляем unique constraint и колонку iso_code
    op.drop_constraint('countries_iso_code_key', 'countries', type_='unique')
    op.drop_column('countries', 'iso_code')
