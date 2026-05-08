"""add refresh_token goal and admin permissions

Revision ID: b5a10313c59b
Revises: db677cf8a2ba
Create Date: 2026-04-15 21:24:15.812276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.constants import (
    REFRESH_TOKEN_GOAL_ID, REFRESH_TOKEN_GOAL_NAME,
    VIEW_RIGHT_ID, EDIT_RIGHT_ID, DELETE_RIGHT_ID
)

# revision identifiers, used by Alembic.
revision: str = 'b5a10313c59b'
down_revision: Union[str, None] = 'db677cf8a2ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


goals_table = sa.sql.table(
    "goals",
    sa.sql.column('id', sa.Integer),
    sa.sql.column('name', sa.String)
)

role_right_goals_table = sa.sql.table(
    "role_right_goals",
    sa.sql.column('role_id', sa.Integer),
    sa.sql.column('right_id', sa.Integer),
    sa.sql.column('goal_id', sa.Integer),
)


def upgrade() -> None:
    global goals_table, role_right_goals_table
    op.bulk_insert(
        goals_table,
        [
            {'id': REFRESH_TOKEN_GOAL_ID, 'name': REFRESH_TOKEN_GOAL_NAME},
        ]
    )
    
    op.bulk_insert(
        role_right_goals_table,
        [
            {'role_id': 1, 'right_id': VIEW_RIGHT_ID, 'goal_id': REFRESH_TOKEN_GOAL_ID},
            {'role_id': 1, 'right_id': EDIT_RIGHT_ID, 'goal_id': REFRESH_TOKEN_GOAL_ID},
            {'role_id': 1, 'right_id': DELETE_RIGHT_ID, 'goal_id': REFRESH_TOKEN_GOAL_ID},
        ]
    )


def downgrade() -> None:
    global goals_table, role_right_goals_table
    op.execute(
        role_right_goals_table.delete()
        .where(role_right_goals_table.c.role_id == 1)
        .where(role_right_goals_table.c.right_id.in_([VIEW_RIGHT_ID, EDIT_RIGHT_ID, DELETE_RIGHT_ID]))
        .where(role_right_goals_table.c.goal_id == REFRESH_TOKEN_GOAL_ID)
    )
    
    op.execute(
        goals_table.delete()
        .where(goals_table.c.id == REFRESH_TOKEN_GOAL_ID)
    )
