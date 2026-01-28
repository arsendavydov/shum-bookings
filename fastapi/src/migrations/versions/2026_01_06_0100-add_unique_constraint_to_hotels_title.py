"""add_unique_constraint_to_hotels_title

Revision ID: add_unique_title
Revises: 0ecbc02df7b8
Create Date: 2026-01-06 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_unique_title'
down_revision: Union[str, None] = "0ecbc02df7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('hotels_title_key', 'hotels', ['title'])


def downgrade() -> None:
    op.drop_constraint('hotels_title_key', 'hotels', type_='unique')

