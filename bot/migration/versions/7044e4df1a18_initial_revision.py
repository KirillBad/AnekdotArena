"""Initial revision

Revision ID: 7044e4df1a18
Revises: c39a27f258fa
Create Date: 2025-02-12 10:45:14.435183

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7044e4df1a18"
down_revision: Union[str, None] = "c39a27f258fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("rates", "rating", existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("rates", "rating", existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###
