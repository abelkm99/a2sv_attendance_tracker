"""added timezone table

Revision ID: b2bd3ceee620
Revises: 64068c3572e1
Create Date: 2024-01-05 16:26:36.004494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2bd3ceee620"
down_revision: Union[str, None] = "64068c3572e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("timezone", sa.String(length=100)))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "timezone")
    # ### end Alembic commands ###
