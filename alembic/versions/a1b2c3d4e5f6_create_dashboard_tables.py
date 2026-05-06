"""Create dashboard tables

Revision ID: a1b2c3d4e5f6
Revises: 213a69474d75
Create Date: 2026-05-06 19:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.models.dashboard import Dashboard, DashboardType  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "213a69474d75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dashboard_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code_name", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code_name"),
    )

    op.create_table(
        "dashboards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("event_type_id", sa.Integer(), nullable=False),
        sa.Column("dashboard_type_id", sa.Integer(), nullable=False),
        sa.Column("title_text", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_type_id"],
            ["event_types.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["dashboard_type_id"],
            ["dashboard_types.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("dashboards")
    op.drop_table("dashboard_types")
