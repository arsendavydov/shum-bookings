"""add_countries_and_cities_tables

Revision ID: 1cbcec213216
Revises: add_unique_title
Create Date: 2026-01-05 23:23:57.291305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1cbcec213216'
down_revision: Union[str, Sequence[str], None] = 'add_unique_title'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицы countries и cities
    op.create_table('countries',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('cities',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('country_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Заполняем countries и cities данными из существующих отелей
    connection = op.get_bind()
    
    # Извлекаем уникальные пары (страна, город) из location
    result = connection.execute(sa.text("""
        SELECT DISTINCT 
            SPLIT_PART(location, ', ', 1) as country,
            SPLIT_PART(location, ', ', 2) as city
        FROM hotels
        WHERE location IS NOT NULL
    """))
    
    country_city_map = {}
    for row in result:
        country_name = row[0]
        city_name = row[1]
        
        # Создаем страну, если её нет
        country_result = connection.execute(
            sa.text("SELECT id FROM countries WHERE name = :name"),
            {"name": country_name}
        )
        country_row = country_result.fetchone()
        
        if country_row is None:
            country_id_result = connection.execute(
                sa.text("INSERT INTO countries (name) VALUES (:name) RETURNING id"),
                {"name": country_name}
            )
            country_id = country_id_result.fetchone()[0]
        else:
            country_id = country_row[0]
        
        # Создаем город, если его нет
        city_result = connection.execute(
            sa.text("SELECT id FROM cities WHERE name = :name AND country_id = :country_id"),
            {"name": city_name, "country_id": country_id}
        )
        city_row = city_result.fetchone()
        
        if city_row is None:
            city_id_result = connection.execute(
                sa.text("INSERT INTO cities (name, country_id) VALUES (:name, :country_id) RETURNING id"),
                {"name": city_name, "country_id": country_id}
            )
            city_id = city_id_result.fetchone()[0]
        else:
            city_id = city_row[0]
        
        country_city_map[(country_name, city_name)] = city_id
    
    # Добавляем city_id и address в hotels (сначала nullable)
    op.add_column('hotels', sa.Column('city_id', sa.Integer(), nullable=True))
    op.add_column('hotels', sa.Column('address', sa.Text(), nullable=True))
    
    # Обновляем hotels: устанавливаем city_id и address из location
    for (country_name, city_name), city_id in country_city_map.items():
        # Извлекаем адрес (всё после "Страна, Город, ")
        pattern = f"{country_name}, {city_name}, "
        connection.execute(
            sa.text("""
                UPDATE hotels 
                SET city_id = :city_id,
                    address = SUBSTRING(location FROM LENGTH(:pattern) + 1)
                WHERE location LIKE :like_pattern
            """),
            {
                "city_id": city_id,
                "pattern": pattern,
                "like_pattern": f"{pattern}%"
            }
        )
    
    # Делаем city_id и address NOT NULL
    op.alter_column('hotels', 'city_id', nullable=False)
    op.alter_column('hotels', 'address', nullable=False)
    
    # Создаем foreign key для hotels.city_id
    op.create_foreign_key('hotels_city_id_fkey', 'hotels', 'cities', ['city_id'], ['id'], ondelete='CASCADE')
    
    # Удаляем старую колонку location
    op.drop_column('hotels', 'location')
    
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
    # Восстанавливаем foreign keys для bookings
    op.drop_constraint('bookings_user_id_fkey', 'bookings', type_='foreignkey')
    op.drop_constraint('bookings_room_id_fkey', 'bookings', type_='foreignkey')
    op.create_foreign_key('bookings_user_id_fkey', 'bookings', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('bookings_room_id_fkey', 'bookings', 'rooms', ['room_id'], ['id'], ondelete='CASCADE')
    
    # Восстанавливаем foreign key для rooms
    op.drop_constraint('rooms_hotel_id_fkey', 'rooms', type_='foreignkey')
    op.create_foreign_key('rooms_hotel_id_fkey', 'rooms', 'hotels', ['hotel_id'], ['id'], ondelete='CASCADE')
    
    # Восстанавливаем колонку location
    op.add_column('hotels', sa.Column('location', sa.TEXT(), autoincrement=False, nullable=True))
    
    # Восстанавливаем location из city и address
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE hotels h
        SET location = c.name || ', ' || ci.name || ', ' || h.address
        FROM cities ci
        JOIN countries c ON ci.country_id = c.id
        WHERE h.city_id = ci.id
    """))
    
    op.alter_column('hotels', 'location', nullable=False)
    
    # Удаляем foreign key и колонки
    op.drop_constraint('hotels_city_id_fkey', 'hotels', type_='foreignkey')
    op.drop_column('hotels', 'address')
    op.drop_column('hotels', 'city_id')
    
    # Удаляем таблицы
    op.drop_table('cities')
    op.drop_table('countries')
