"""add_bookings_table_and_check_in_out_times_to_hotels

Revision ID: add_bookings_check_in_out
Revises: 79f7068076a2
Create Date: 2025-01-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_bookings_check_in_out'
down_revision: Union[str, Sequence[str], None] = '79f7068076a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем поля check_in_time и check_out_time в таблицу hotels
    op.add_column('hotels', sa.Column('check_in_time', sa.Time(), nullable=True, server_default='14:00:00'))
    op.add_column('hotels', sa.Column('check_out_time', sa.Time(), nullable=True, server_default='12:00:00'))
    
    # Создаем таблицу bookings
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date_from', sa.Date(), nullable=False),
        sa.Column('date_to', sa.Date(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем таблицу bookings
    op.drop_table('bookings')
    
    # Удаляем поля check_in_time и check_out_time из таблицы hotels
    op.drop_column('hotels', 'check_out_time')
    op.drop_column('hotels', 'check_in_time')

