"""added report_count column to Anecdote

Revision ID: b99b6b318144
Revises: 7044e4df1a18
Create Date: 2025-02-12 11:05:49.093217

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b99b6b318144"
down_revision: Union[str, None] = "7044e4df1a18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
