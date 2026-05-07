"""Seed dashboard_types dictionary

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-05-06 19:05:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    dashboard_types = sa.sql.table(
        "dashboard_types",
        sa.sql.column("id", sa.Integer),
        sa.sql.column("code_name", sa.String(length=20)),
        sa.sql.column("description", sa.String(length=100)),
    )

    op.bulk_insert(
        dashboard_types,
        [
            {"id": 1, "code_name": "chart", "description": "График статистики"},
            {"id": 2, "code_name": "avg", "description": "Агрегированная статистика"},
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM dashboard_types WHERE code_name IN ('chart', 'avg')"
    )
