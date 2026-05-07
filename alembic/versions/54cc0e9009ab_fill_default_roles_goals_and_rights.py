"""Fill default roles, goals and rights

Revision ID: 54cc0e9009ab
Revises: 63ec4b49750b
Create Date: 2025-10-12 14:05:01.662031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# static data

goals: dict[int, str] = {
    1: "stats",
    2: "dashboards",
    3: "users",
    4: "roles",
    5: "tables",
    6: "resources",
    7: "tasks",
    8: "nav_data"
}

rights: dict[int, str] = {
    1: "view",
    2: "create",
    3: "edit",
    4: "delete",
    5: "grant"
}

roles: dict[int, str] = {
    1: "admin"
}

roles_rights_goals: list[tuple[int, int, int]] = [
    (1, 1, 1),
    (1, 1, 2),
    (1, 1, 3),
    (1, 2, 3),
    (1, 3, 3),
    (1, 4, 3),
    (1, 1, 4),
    (1, 2, 4),
    (1, 3, 4),
    (1, 4, 4),
    (1, 5, 4),
    (1, 1, 5),
    (1, 3, 5),
    (1, 1, 6),
    (1, 2, 6),
    (1, 3, 6),
    (1, 4, 6),
    (1, 1, 7),
    (1, 3, 7),
    (1, 1, 8),
    (1, 2, 8),
    (1, 3, 8),
    (1, 4, 8),
]

# revision identifiers, used by Alembic.
revision: str = '54cc0e9009ab'
down_revision: Union[str, None] = '63ec4b49750b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def data_upgrades():
    goals_table = sa.sql.table(
        "goals",
        sa.sql.column('id', sa.Integer),
        sa.sql.column('name', sa.String)
    )
    rights_table = sa.sql.table(
        "rights",
        sa.sql.column('id', sa.Integer),
        sa.sql.column('name', sa.String)
    )

    roles_table = sa.sql.table(
        "roles",
        sa.sql.column('id', sa.Integer),
        sa.sql.column('name', sa.String)
    )

    role_right_goals_table = sa.sql.table(
        "role_right_goals",
        sa.sql.column('role_id', sa.Integer),
        sa.sql.column('right_id', sa.Integer),
        sa.sql.column('goal_id', sa.Integer),
    )

    op.bulk_insert(
        goals_table,
        list([{'id': key, 'name': value} for key, value in goals.items()])
    )
    op.bulk_insert(
        rights_table,
        list([{'id': key, 'name': value} for key, value in rights.items()])
    )
    op.bulk_insert(
        roles_table,
        list([{'id': key, 'name': value} for key, value in roles.items()])
    )
    op.bulk_insert(
        role_right_goals_table,
        list([{'role_id': x[0], 'right_id': x[1], 'goal_id': x[2]} for x in roles_rights_goals])
    )


def upgrade() -> None:
    data_upgrades()


def downgrade() -> None:
    pass
