"""Add dashboard permissions to admin role

Revision ID: c3d4e5f6a1b2
Revises: b2c3d4e5f6a1
Create Date: 2026-05-06 19:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.constants import (
    DASHBOARDS_GOAL_ID,
    CREATE_RIGHT_ID,
    EDIT_RIGHT_ID,
    DELETE_RIGHT_ID,
)


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a1b2"
down_revision: Union[str, None] = "b2c3d4e5f6a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ADMIN_ROLE_ID = 1


def _role_right_goals_table() -> sa.Table:
    return sa.sql.table(
        "role_right_goals",
        sa.sql.column("role_id", sa.Integer),
        sa.sql.column("right_id", sa.Integer),
        sa.sql.column("goal_id", sa.Integer),
        sa.sql.column("can_grant", sa.Boolean),
    )


def upgrade() -> None:
    role_right_goals_table = _role_right_goals_table()
    op.bulk_insert(
        role_right_goals_table,
        [
            {
                "role_id": ADMIN_ROLE_ID,
                "right_id": CREATE_RIGHT_ID,
                "goal_id": DASHBOARDS_GOAL_ID,
                "can_grant": True,
            },
            {
                "role_id": ADMIN_ROLE_ID,
                "right_id": EDIT_RIGHT_ID,
                "goal_id": DASHBOARDS_GOAL_ID,
                "can_grant": True,
            },
            {
                "role_id": ADMIN_ROLE_ID,
                "right_id": DELETE_RIGHT_ID,
                "goal_id": DASHBOARDS_GOAL_ID,
                "can_grant": True,
            },
        ],
    )


def downgrade() -> None:
    role_right_goals_table = _role_right_goals_table()
    op.execute(
        role_right_goals_table.delete()
        .where(role_right_goals_table.c.role_id == ADMIN_ROLE_ID)
        .where(
            role_right_goals_table.c.right_id.in_(
                [CREATE_RIGHT_ID, EDIT_RIGHT_ID, DELETE_RIGHT_ID]
            )
        )
        .where(role_right_goals_table.c.goal_id == DASHBOARDS_GOAL_ID)
    )
