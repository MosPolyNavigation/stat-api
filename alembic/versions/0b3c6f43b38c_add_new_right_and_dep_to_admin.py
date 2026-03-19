"""Add new goal user_pass and edit right for admin

Revision ID: 0b3c6f43b38c
Revises: 84c9b51dc5fc
Create Date: 2026-03-19 15:03:10.013399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b3c6f43b38c'
down_revision: Union[str, None] = '84c9b51dc5fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # === Таблицы для вставки данных ===
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
    
    # === 1. Добавляем новую цель user_pass (ID: 9) ===
    op.bulk_insert(
        goals_table,
        [{'id': 9, 'name': 'user_pass'}]
    )
    
    # === 2. Добавляем право edit (3) для admin (1) на цель user_pass (9) ===
    op.bulk_insert(
        role_right_goals_table,
        [{'role_id': 1, 'right_id': 3, 'goal_id': 9}]
    )


def downgrade() -> None:
    # === Таблицы для удаления данных ===
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
    
    # === 1. Удаляем связь role_right_goal ===
    op.execute(
        role_right_goals_table.delete()
        .where(role_right_goals_table.c.role_id == 1)
        .where(role_right_goals_table.c.right_id == 3)
        .where(role_right_goals_table.c.goal_id == 9)
    )
    
    # === 2. Удаляем цель user_pass ===
    op.execute(
        goals_table.delete()
        .where(goals_table.c.id == 9)
    )
