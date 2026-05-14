"""Добавление прав stats и связи reviews с client_ids

Revision ID: e2f4a6b8c0d1
Revises: d38504baa564
Create Date: 2026-04-29 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2f4a6b8c0d1"
down_revision: Union[str, None] = "d38504baa564"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("reviews") as batch_op:
        batch_op.add_column(sa.Column("client_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_reviews_client_id",
            "client_ids",
            ["client_id"],
            ["id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
        batch_op.drop_column("user_id")


def downgrade() -> None:
    with op.batch_alter_table("reviews") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(length=36), nullable=False))
        batch_op.create_foreign_key(
            "fk_reviews_user_id",
            "user_ids",
            ["user_id"],
            ["user_id"],
        )
        batch_op.drop_constraint("fk_reviews_client_id", type_="foreignkey")
        batch_op.drop_column("client_id")
