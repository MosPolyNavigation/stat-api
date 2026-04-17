"""add refresh_token goal and admin permissions

Revision ID: b5a10313c59b
Revises: 82ace2d0f349
Create Date: 2026-04-15 21:24:15.812276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5a10313c59b'
down_revision: Union[str, None] = '82ace2d0f349'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


goals = sa.table(
    "goals",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)

roles = sa.table(
    "roles",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)

rights = sa.table(
    "rights",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)

role_right_goals = sa.table(
    "role_right_goals",
    sa.column("role_id", sa.Integer),
    sa.column("right_id", sa.Integer),
    sa.column("goal_id", sa.Integer),
)


def upgrade() -> None:
    connection = op.get_bind()

    goal_id = connection.execute(
        sa.select(goals.c.id).where(goals.c.name == "refresh_token")
    ).scalar_one_or_none()

    if goal_id is None:
        connection.execute(
            sa.insert(goals).values(name="refresh_token")
        )
        goal_id = connection.execute(
            sa.select(goals.c.id).where(goals.c.name == "refresh_token")
        ).scalar_one()

    admin_role_id = connection.execute(
        sa.select(roles.c.id).where(roles.c.name == "admin")
    ).scalar_one()

    right_rows = connection.execute(
        sa.select(rights.c.id, rights.c.name).where(
            rights.c.name.in_(["view", "edit", "delete"])
        )
    ).all()

    for right_row in right_rows:
        exists = connection.execute(
            sa.select(role_right_goals.c.role_id).where(
                role_right_goals.c.role_id == admin_role_id,
                role_right_goals.c.right_id == right_row.id,
                role_right_goals.c.goal_id == goal_id,
            )
        ).scalar_one_or_none()

        if exists is None:
            connection.execute(
                sa.insert(role_right_goals).values(
                    role_id=admin_role_id,
                    right_id=right_row.id,
                    goal_id=goal_id,
                )
            )


def downgrade() -> None:
    connection = op.get_bind()

    goal_id = connection.execute(
        sa.select(goals.c.id).where(goals.c.name == "refresh_token")
    ).scalar_one_or_none()

    if goal_id is None:
        return

    admin_role_id = connection.execute(
        sa.select(roles.c.id).where(roles.c.name == "admin")
    ).scalar_one_or_none()

    right_ids = connection.execute(
        sa.select(rights.c.id).where(
            rights.c.name.in_(["view", "edit", "delete"])
        )
    ).scalars().all()

    if admin_role_id is not None and right_ids:
        connection.execute(
            sa.delete(role_right_goals).where(
                role_right_goals.c.role_id == admin_role_id,
                role_right_goals.c.goal_id == goal_id,
                role_right_goals.c.right_id.in_(right_ids),
            )
        )

    connection.execute(
        sa.delete(goals).where(goals.c.id == goal_id)
    )