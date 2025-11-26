"""Fill default roles, goals and rights

Revision ID: 54cc0e9009ab
Revises: 63ec4b49750b
Create Date: 2025-10-12 14:05:01.662031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.helpers.data import roles, rights, goals, roles_rights_goals

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
