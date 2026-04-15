"""Create new event system tables

Revision ID: c1a2f3e4d5b6
Revises: db677cf8a2ba
Create Date: 2026-04-15 21:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1a2f3e4d5b6"
down_revision: Union[str, None] = "db677cf8a2ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code_name", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code_name"),
    )

    op.create_table(
        "client_ids",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ident", sa.String(length=36), nullable=False),
        sa.Column("creation_date", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ident"),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("event_type_id", sa.Integer(), nullable=False),
        sa.Column("trigger_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["client_ids.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["event_type_id"],
            ["event_types.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "value_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "payload_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code_name", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=True),
        sa.Column("value_type_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["value_type_id"],
            ["value_types.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code_name"),
    )

    op.create_table(
        "payloads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("type_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["payload_types.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "allowed_payloads",
        sa.Column("event_type_id", sa.Integer(), nullable=False),
        sa.Column("payload_type_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_type_id"],
            ["event_types.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["payload_type_id"],
            ["payload_types.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("event_type_id", "payload_type_id"),
    )


def downgrade() -> None:
    op.drop_table("allowed_payloads")
    op.drop_table("payloads")
    op.drop_table("payload_types")
    op.drop_table("value_types")
    op.drop_table("events")
    op.drop_table("client_ids")
    op.drop_table("event_types")
