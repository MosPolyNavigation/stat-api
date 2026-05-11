"""Add aud_photo table and drop photo_id from auditories

Revision ID: f3b1f4129f0e
Revises: 6080e7ca7e97
Create Date: 2026-03-01 12:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3b1f4129f0e"
down_revision: Union[str, None] = "6080e7ca7e97"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "aud_photo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("aud_id", sa.Integer(), nullable=False),
        sa.Column("ext", sa.String(length=6), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("link", sa.String(length=255), nullable=False),
        sa.Column("creation_date", sa.DateTime(), nullable=False),
        sa.Column("update_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["aud_id"], ["auditories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    with op.batch_alter_table("auditories") as batch_op:
        batch_op.drop_column("photo_id")


def downgrade() -> None:
    with op.batch_alter_table("auditories") as batch_op:
        batch_op.add_column(sa.Column("photo_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_auditories_photo_id_statics",
            "statics",
            ["photo_id"],
            ["id"],
        )

    op.drop_table("aud_photo")
