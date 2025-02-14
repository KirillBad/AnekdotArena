"""report added 2

Revision ID: 3807840ebda5
Revises: 448464d2bdf0
Create Date: 2025-02-12 11:44:36.510863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3807840ebda5'
down_revision: Union[str, None] = '448464d2bdf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('anecdotes', sa.Column('report_count', sa.Integer(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('anecdotes', 'report_count')
    # ### end Alembic commands ###
