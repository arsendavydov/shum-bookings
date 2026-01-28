"""add_created_at_to_bookings

Revision ID: 0ecbc02df7b8
Revises: add_cascade_delete
Create Date: 2026-01-06 00:49:49.957747

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0ecbc02df7b8"
down_revision: Union[str, Sequence[str], None] = "add_cascade_delete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'bookings',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('bookings', 'created_at')
