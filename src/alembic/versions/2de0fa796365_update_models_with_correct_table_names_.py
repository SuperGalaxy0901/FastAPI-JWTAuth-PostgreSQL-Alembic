"""Update models with correct table names and relationships

Revision ID: 2de0fa796365
Revises: 8e462966929c
Create Date: 2024-09-11 18:35:14.523766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2de0fa796365'
down_revision: Union[str, None] = '8e462966929c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscriptions', 'price')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscriptions', sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
