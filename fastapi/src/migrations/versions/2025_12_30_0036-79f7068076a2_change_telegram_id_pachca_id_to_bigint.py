"""change_telegram_id_pachca_id_to_bigint

Revision ID: 79f7068076a2
Revises: aff4a2463ebf
Create Date: 2025-12-30 00:36:37.728133

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79f7068076a2'
down_revision: Union[str, Sequence[str], None] = 'aff4a2463ebf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Изменяем тип telegram_id с VARCHAR на BIGINT
    # Сначала удаляем все строковые значения, которые нельзя преобразовать в числа
    op.execute("UPDATE users SET telegram_id = NULL WHERE telegram_id IS NOT NULL AND telegram_id !~ '^[0-9]+$'")
    op.execute("UPDATE users SET pachca_id = NULL WHERE pachca_id IS NOT NULL AND pachca_id !~ '^[0-9]+$'")
    
    # Изменяем тип колонок
    op.alter_column(
        "users", 
        "telegram_id", 
        type_=sa.BigInteger(),
        existing_type=sa.VARCHAR(length=100),
        nullable=True,
        postgresql_using="telegram_id::bigint"
    )
    op.alter_column(
        "users", 
        "pachca_id", 
        type_=sa.BigInteger(),
        existing_type=sa.VARCHAR(length=100),
        nullable=True,
        postgresql_using="pachca_id::bigint"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем тип обратно в VARCHAR
    op.alter_column(
        "users", 
        "telegram_id", 
        type_=sa.VARCHAR(length=100),
        existing_type=sa.BigInteger(),
        nullable=True,
        postgresql_using="telegram_id::text"
    )
    op.alter_column(
        "users", 
        "pachca_id", 
        type_=sa.VARCHAR(length=100),
        existing_type=sa.BigInteger(),
        nullable=True,
        postgresql_using="pachca_id::text"
    )
