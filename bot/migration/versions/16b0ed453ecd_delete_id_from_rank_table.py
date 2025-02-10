"""delete id from rank table

Revision ID: 16b0ed453ecd
Revises: 011eeb7727c6
Create Date: 2025-02-10 03:45:15.742762

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "16b0ed453ecd"
down_revision: Union[str, None] = "011eeb7727c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Сначала удаляем primary key constraint
    op.drop_constraint("rates_pkey", "rates", type_="primary")

    # Удаляем колонку id
    op.drop_column("rates", "id")

    # Создаем новый primary key только из anecdote_id и user_id
    op.create_primary_key("rates_pkey", "rates", ["anecdote_id", "user_id"])


def downgrade() -> None:
    # В случае отката добавляем колонку id обратно
    op.drop_constraint("rates_pkey", "rates", type_="primary")

    op.add_column(
        "rates", sa.Column("id", sa.Integer(), autoincrement=True, nullable=False)
    )

    op.create_primary_key("rates_pkey", "rates", ["anecdote_id", "user_id", "id"])
