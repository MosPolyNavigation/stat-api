"""Add stats dictionary rights and move reviews to client_ids

Revision ID: f4b6a9d2c8e1
Revises: d7e8f9a0b1c2
Create Date: 2026-04-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f4b6a9d2c8e1"
down_revision: Union[str, None] = "d7e8f9a0b1c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


role_right_goals = sa.sql.table(
    "role_right_goals",
    sa.sql.column("role_id", sa.Integer),
    sa.sql.column("right_id", sa.Integer),
    sa.sql.column("goal_id", sa.Integer),
)


def upgrade() -> None:
    op.bulk_insert(
        role_right_goals,
        [
            {"role_id": 1, "right_id": 2, "goal_id": 1},
            {"role_id": 1, "right_id": 3, "goal_id": 1},
            {"role_id": 1, "right_id": 4, "goal_id": 1},
        ],
    )

    with op.batch_alter_table("reviews") as batch_op:
        batch_op.add_column(sa.Column("client_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_reviews_client_id_client_ids",
            "client_ids",
            ["client_id"],
            ["id"],
        )

    op.execute(
        """
        INSERT INTO client_ids (ident, creation_date)
        SELECT u.user_id, u.creation_date
        FROM user_ids u
        WHERE EXISTS (
            SELECT 1 FROM reviews r WHERE r.user_id = u.user_id
        )
        AND NOT EXISTS (
            SELECT 1 FROM client_ids c WHERE c.ident = u.user_id
        )
        """
    )
    op.execute(
        """
        UPDATE reviews
        SET client_id = (
            SELECT c.id FROM client_ids c WHERE c.ident = reviews.user_id
        )
        WHERE client_id IS NULL
        """
    )

    with op.batch_alter_table("reviews") as batch_op:
        batch_op.alter_column("client_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column("user_id")


def downgrade() -> None:
    with op.batch_alter_table("reviews") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            "fk_reviews_user_id_user_ids",
            "user_ids",
            ["user_id"],
            ["user_id"],
        )

    op.execute(
        """
        UPDATE reviews
        SET user_id = (
            SELECT c.ident FROM client_ids c WHERE c.id = reviews.client_id
        )
        WHERE user_id IS NULL
        """
    )

    with op.batch_alter_table("reviews") as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.String(length=36), nullable=False)
        batch_op.drop_column("client_id")

    op.execute(
        """
        DELETE FROM role_right_goals
        WHERE role_id = 1
          AND goal_id = 1
          AND right_id IN (2, 3, 4)
        """
    )
