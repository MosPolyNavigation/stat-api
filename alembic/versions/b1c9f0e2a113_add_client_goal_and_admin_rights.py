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


RIGHT_NAMES = ("view", "create", "edit", "delete")


def _get_or_create_goal_id(bind, goal_name: str) -> int:
    goal_id = bind.execute(
        sa.text("SELECT id FROM goals WHERE name = :name"),
        {"name": goal_name},
    ).scalar()

    if goal_id is not None:
        return int(goal_id)

    bind.execute(
        sa.text("INSERT INTO goals (name) VALUES (:name)"),
        {"name": goal_name},
    )
    created_goal_id = bind.execute(
        sa.text("SELECT id FROM goals WHERE name = :name"),
        {"name": goal_name},
    ).scalar()
    return int(created_goal_id)


def _get_or_create_right_id(bind, right_name: str) -> int:
    right_id = bind.execute(
        sa.text("SELECT id FROM rights WHERE name = :name"),
        {"name": right_name},
    ).scalar()

    if right_id is not None:
        return int(right_id)

    bind.execute(
        sa.text("INSERT INTO rights (name) VALUES (:name)"),
        {"name": right_name},
    )
    created_right_id = bind.execute(
        sa.text("SELECT id FROM rights WHERE name = :name"),
        {"name": right_name},
    ).scalar()
    return int(created_right_id)


def upgrade() -> None:
    bind = op.get_bind()
    client_goal_id = _get_or_create_goal_id(bind, "client")

    for right_name in RIGHT_NAMES:
        right_id = _get_or_create_right_id(bind, right_name)
        bind.execute(
            sa.text(
                """
                INSERT INTO role_right_goals (role_id, right_id, goal_id)
                SELECT :role_id, :right_id, :goal_id
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM role_right_goals
                    WHERE role_id = :role_id
                      AND right_id = :right_id
                      AND goal_id = :goal_id
                )
                """
            ),
            {
                "role_id": 1,
                "right_id": right_id,
                "goal_id": client_goal_id,
            },
        )


def downgrade() -> None:
    bind = op.get_bind()
    client_goal_id = bind.execute(
        sa.text("SELECT id FROM goals WHERE name = :name"),
        {"name": "client"},
    ).scalar()

    if client_goal_id is None:
        return

    right_ids = bind.execute(
        sa.text(
            "SELECT id FROM rights WHERE name IN ('view', 'create', 'edit', 'delete')"
        )
    ).scalars().all()

    if right_ids:
        bind.execute(
            sa.text(
                """
                DELETE FROM role_right_goals
                WHERE role_id = :role_id
                  AND goal_id = :goal_id
                  AND right_id IN :right_ids
                """
            ).bindparams(sa.bindparam("right_ids", expanding=True)),
            {
                "role_id": 1,
                "goal_id": int(client_goal_id),
                "right_ids": list(right_ids),
            },
        )

    bind.execute(
        sa.text("DELETE FROM goals WHERE id = :goal_id"),
        {"goal_id": int(client_goal_id)},
    )

    # Remove rights only if they are no longer used anywhere.
    bind.execute(
        sa.text(
            """
            DELETE FROM rights
            WHERE name IN ('view', 'create', 'edit', 'delete')
              AND id NOT IN (SELECT DISTINCT right_id FROM role_right_goals)
            """
        )
    )

