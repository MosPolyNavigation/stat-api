"""Add client goal and admin permissions

Revision ID: b1c9f0e2a113
Revises: d7e8f9a0b1c2
Create Date: 2026-04-22 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1c9f0e2a113"
down_revision: Union[str, None] = "d7e8f9a0b1c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CLIENT_GOAL_ID = 12
ADMIN_ROLE_ID = 1
CREATE_RIGHT_ID = 2


def upgrade() -> None:
    goals_table = sa.sql.table(
        "goals",
        sa.sql.column("id", sa.Integer),
        sa.sql.column("name", sa.String),
    )
    role_right_goals_table = sa.sql.table(
        "role_right_goals",
        sa.sql.column("role_id", sa.Integer),
        sa.sql.column("right_id", sa.Integer),
        sa.sql.column("goal_id", sa.Integer),
    )

    op.bulk_insert(
        goals_table,
        [{"id": CLIENT_GOAL_ID, "name": "client"}],
    )

    op.bulk_insert(
        role_right_goals_table,
        [
            {
                "role_id": ADMIN_ROLE_ID,
                "right_id": CREATE_RIGHT_ID,
                "goal_id": CLIENT_GOAL_ID,
            }
        ],
    )


def downgrade() -> None:
    goals_table = sa.sql.table(
        "goals",
        sa.sql.column("id", sa.Integer),
        sa.sql.column("name", sa.String),
    )
    role_right_goals_table = sa.sql.table(
        "role_right_goals",
        sa.sql.column("role_id", sa.Integer),
        sa.sql.column("right_id", sa.Integer),
        sa.sql.column("goal_id", sa.Integer),
    )

    op.execute(
        role_right_goals_table.delete()
        .where(role_right_goals_table.c.role_id == ADMIN_ROLE_ID)
        .where(role_right_goals_table.c.right_id == CREATE_RIGHT_ID)
        .where(role_right_goals_table.c.goal_id == CLIENT_GOAL_ID)
    )

    op.execute(
        goals_table.delete()
        .where(goals_table.c.id == CLIENT_GOAL_ID)
    )
