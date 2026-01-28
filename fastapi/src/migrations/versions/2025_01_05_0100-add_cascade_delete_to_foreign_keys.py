"""add_cascade_delete_to_foreign_keys

Revision ID: add_cascade_delete
Revises: add_bookings_check_in_out
Create Date: 2025-01-05 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_cascade_delete'
down_revision: Union[str, Sequence[str], None] = 'add_bookings_check_in_out'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем старые внешние ключи
    op.drop_constraint('rooms_hotel_id_fkey', 'rooms', type_='foreignkey')
    op.drop_constraint('bookings_room_id_fkey', 'bookings', type_='foreignkey')
    op.drop_constraint('bookings_user_id_fkey', 'bookings', type_='foreignkey')
    
    # Создаем новые внешние ключи с CASCADE DELETE
    op.create_foreign_key(
        'rooms_hotel_id_fkey',
        'rooms', 'hotels',
        ['hotel_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'bookings_room_id_fkey',
        'bookings', 'rooms',
        ['room_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'bookings_user_id_fkey',
        'bookings', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем внешние ключи с CASCADE
    op.drop_constraint('bookings_user_id_fkey', 'bookings', type_='foreignkey')
    op.drop_constraint('bookings_room_id_fkey', 'bookings', type_='foreignkey')
    op.drop_constraint('rooms_hotel_id_fkey', 'rooms', type_='foreignkey')
    
    # Восстанавливаем старые внешние ключи без CASCADE
    op.create_foreign_key(
        'rooms_hotel_id_fkey',
        'rooms', 'hotels',
        ['hotel_id'], ['id']
    )
    op.create_foreign_key(
        'bookings_room_id_fkey',
        'bookings', 'rooms',
        ['room_id'], ['id']
    )
    op.create_foreign_key(
        'bookings_user_id_fkey',
        'bookings', 'users',
        ['user_id'], ['id']
    )

