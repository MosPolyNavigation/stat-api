"""Create DOD-prefixed navigation tables

Revision ID: 1d4cf4d7f8aa
Revises: f3b1f4129f0e
Create Date: 2026-03-11 13:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1d4cf4d7f8aa"
down_revision: Union[str, None] = "f3b1f4129f0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dod_floors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "dod_locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_sys", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=25), nullable=False),
        sa.Column("short", sa.String(length=2), nullable=False),
        sa.Column("ready", sa.Boolean(), nullable=False),
        sa.Column("address", sa.String(length=100), nullable=False),
        sa.Column("metro", sa.String(length=100), nullable=False),
        sa.Column("crossings", sa.Text(), nullable=True),
        sa.Column("comments", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id_sys"),
    )

    op.create_table(
        "dod_statics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ext", sa.String(length=6), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("link", sa.String(length=255), nullable=False),
        sa.Column("creation_date", sa.DateTime(), nullable=False),
        sa.Column("update_date", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "dod_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "dod_corpuses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_sys", sa.String(length=7), nullable=False),
        sa.Column("loc_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("ready", sa.Boolean(), nullable=False),
        sa.Column("stair_groups", sa.Text(), nullable=True),
        sa.Column("comments", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["loc_id"], ["dod_locations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id_sys"),
    )

    op.create_table(
        "dod_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_sys", sa.String(length=20), nullable=False),
        sa.Column("cor_id", sa.Integer(), nullable=False),
        sa.Column("floor_id", sa.Integer(), nullable=False),
        sa.Column("ready", sa.Boolean(), nullable=False),
        sa.Column("entrances", sa.Text(), nullable=False),
        sa.Column("graph", sa.Text(), nullable=False),
        sa.Column("svg_id", sa.Integer(), nullable=True),
        sa.Column("nearest_entrance", sa.String(length=50), nullable=True),
        sa.Column("nearest_man_wc", sa.String(length=50), nullable=True),
        sa.Column("nearest_woman_wc", sa.String(length=50), nullable=True),
        sa.Column("nearest_shared_wc", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["cor_id"], ["dod_corpuses.id"]),
        sa.ForeignKeyConstraint(["floor_id"], ["dod_floors.id"]),
        sa.ForeignKeyConstraint(["svg_id"], ["dod_statics.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id_sys"),
    )

    op.create_table(
        "dod_auditories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_sys", sa.String(length=50), nullable=False),
        sa.Column("type_id", sa.Integer(), nullable=False),
        sa.Column("ready", sa.Boolean(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("text_from_sign", sa.String(length=200), nullable=True),
        sa.Column("additional_info", sa.String(length=200), nullable=True),
        sa.Column("comments", sa.String(length=200), nullable=True),
        sa.Column("link", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["dod_plans.id"]),
        sa.ForeignKeyConstraint(["type_id"], ["dod_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dod_aud_photo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("aud_id", sa.Integer(), nullable=False),
        sa.Column("ext", sa.String(length=6), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("link", sa.String(length=255), nullable=False),
        sa.Column("creation_date", sa.DateTime(), nullable=False),
        sa.Column("update_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["aud_id"], ["dod_auditories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.bulk_insert(
        sa.sql.table(
            "dod_floors",
            sa.sql.column("id", sa.Integer),
            sa.sql.column("name", sa.Integer),
        ),
        [{"id": x + 2, "name": x} for x in range(-1, 10)],
    )


def downgrade() -> None:
    op.drop_table("dod_aud_photo")
    op.drop_table("dod_auditories")
    op.drop_table("dod_plans")
    op.drop_table("dod_corpuses")
    op.drop_table("dod_types")
    op.drop_table("dod_statics")
    op.drop_table("dod_locations")
    op.drop_table("dod_floors")
