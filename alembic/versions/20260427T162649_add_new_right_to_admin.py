"""Add new right to admin

Revision ID: d32be1432554
Revises: d38504baa564
Create Date: 2026-04-27 16:26:49.233414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.constants import (
    TASKS_GOAL_ID,
    CREATE_RIGHT_ID, DELETE_RIGHT_ID
)

# revision identifiers, used by Alembic.
revision: str = 'd32be1432554'
down_revision: Union[str, None] = 'd38504baa564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_right_goals_table = sa.sql.table(
    "role_right_goals",
    sa.sql.column('role_id', sa.Integer),
    sa.sql.column('right_id', sa.Integer),
    sa.sql.column('goal_id', sa.Integer),
)


def upgrade() -> None:
    global role_right_goals_table
    
    op.bulk_insert(
        role_right_goals_table,
        [
            {'role_id': 1, 'right_id': CREATE_RIGHT_ID, 'goal_id': TASKS_GOAL_ID},
            {'role_id': 1, 'right_id': DELETE_RIGHT_ID, 'goal_id': TASKS_GOAL_ID},
        ]
    )


def downgrade() -> None:
    global role_right_goals_table
    op.execute(
        role_right_goals_table.delete()
        .where(role_right_goals_table.c.role_id == 1)
        .where(role_right_goals_table.c.right_id.in_([CREATE_RIGHT_ID, DELETE_RIGHT_ID]))
        .where(role_right_goals_table.c.goal_id == TASKS_GOAL_ID)
    )
