"""Added StartWay model

Revision ID: 266183bb48a0
Revises: fa5a0267aace
Create Date: 2025-01-04 02:58:55.244533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '266183bb48a0'
down_revision: Union[str, None] = 'fa5a0267aace'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'started_ways',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('visit_date', sa.DateTime(), nullable=False),
        sa.Column('start_id', sa.String(length=50), nullable=False),
        sa.Column('end_id', sa.String(length=50), nullable=False),
        # sa.ForeignKeyConstraint(['end_id'], ['auditories.id'], ),
        # sa.ForeignKeyConstraint(['start_id'], ['auditories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user_ids.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_started_ways_id'),
        'started_ways',
        ['id'],
        unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_started_ways_id'), table_name='started_ways')
    op.drop_table('started_ways')
    # ### end Alembic commands ###
