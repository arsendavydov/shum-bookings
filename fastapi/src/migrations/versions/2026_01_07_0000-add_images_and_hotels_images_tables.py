"""add images and hotels_images tables

Revision ID: abc123def456
Revises: 0ecbc02df7b8
Create Date: 2026-01-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_images_tables'
down_revision: Union[str, None] = 'add_facilities_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу images
    op.create_table(
        'images',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем промежуточную таблицу hotels_images
    op.create_table(
        'hotels_images',
        sa.Column('hotel_id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('hotel_id', 'image_id')
    )


def downgrade() -> None:
    # Удаляем промежуточную таблицу
    op.drop_table('hotels_images')
    
    # Удаляем таблицу images
    op.drop_table('images')

