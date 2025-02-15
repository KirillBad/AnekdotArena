"""delete anecdote_id field in gift table

Revision ID: aa6a247cc4a9
Revises: adbdb3335f1c
Create Date: 2025-02-15 02:04:52.599764

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aa6a247cc4a9"
down_revision: Union[str, None] = "adbdb3335f1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("gifts_anecdote_id_fkey", "gifts", type_="foreignkey")
    op.drop_column("gifts", "anecdote_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "gifts",
        sa.Column("anecdote_id", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.create_foreign_key(
        "gifts_anecdote_id_fkey", "gifts", "anecdotes", ["anecdote_id"], ["id"]
    )
    # ### end Alembic commands ###
