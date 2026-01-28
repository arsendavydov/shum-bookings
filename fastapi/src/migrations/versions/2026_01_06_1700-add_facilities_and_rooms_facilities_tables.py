"""add_facilities_and_rooms_facilities_tables

Revision ID: add_facilities_tables
Revises: add_unique_title
Create Date: 2026-01-06 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_facilities_tables'
down_revision: Union[str, None] = '6a9c464e621c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу facilities
    op.create_table(
        'facilities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем промежуточную таблицу rooms_facilities для many-to-many связи
    op.create_table(
        'rooms_facilities',
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('room_id', 'facility_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем промежуточную таблицу
    op.drop_table('rooms_facilities')
    
    # Удаляем таблицу facilities
    op.drop_table('facilities')

