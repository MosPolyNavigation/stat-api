"""Добавление прав stats и связи reviews с client_ids

Revision ID: e2f4a6b8c0d1
Revises: b1c9f0e2a113
Create Date: 2026-04-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2f4a6b8c0d1"
down_revision: Union[str, None] = "b1c9f0e2a113"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ADMIN_ROLE_ID = 1
STATS_GOAL_ID = 1
CREATE_RIGHT_ID = 2
EDIT_RIGHT_ID = 3
DELETE_RIGHT_ID = 4


def _role_right_goals_table() -> sa.Table:
    return sa.sql.table(
        "role_right_goals",
        sa.sql.column("role_id", sa.Integer),
        sa.sql.column("right_id", sa.Integer),
        sa.sql.column("goal_id", sa.Integer),
    )


def upgrade() -> None:
    role_right_goals_table = _role_right_goals_table()
    op.bulk_insert(
        role_right_goals_table,
        [
            {
                "role_id": ADMIN_ROLE_ID,
                "right_id": CREATE_RIGHT_ID,
                "goal_id": STATS_GOAL_ID,
            },
            {
                "role_id": ADMIN_ROLE_ID,
                "right_id": EDIT_RIGHT_ID,
                "goal_id": STATS_GOAL_ID,
            },
            {
                "role_id": ADMIN_ROLE_ID,
                "right_id": DELETE_RIGHT_ID,
                "goal_id": STATS_GOAL_ID,
            },
        ],
    )

    op.execute(
        """
        INSERT INTO client_ids (id, ident, creation_date)
        SELECT
            (SELECT COALESCE(MAX(id), 0) FROM client_ids)
                + ROW_NUMBER() OVER (ORDER BY reviews.user_id),
            reviews.user_id,
            MIN(reviews.creation_date)
        FROM reviews
        LEFT JOIN client_ids ON client_ids.ident = reviews.user_id
        WHERE client_ids.id IS NULL
        GROUP BY reviews.user_id
        """
    )

    with op.batch_alter_table("reviews") as batch_op:
        batch_op.add_column(sa.Column("client_id", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE reviews
        SET client_id = (
            SELECT client_ids.id
            FROM client_ids
            WHERE client_ids.ident = reviews.user_id
        )
        """
    )

    with op.batch_alter_table("reviews") as batch_op:
        batch_op.alter_column("client_id", existing_type=sa.Integer(), nullable=False)
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
    role_right_goals_table = _role_right_goals_table()
    op.execute(
        role_right_goals_table.delete()
        .where(role_right_goals_table.c.role_id == ADMIN_ROLE_ID)
        .where(role_right_goals_table.c.right_id.in_([CREATE_RIGHT_ID, EDIT_RIGHT_ID, DELETE_RIGHT_ID]))
        .where(role_right_goals_table.c.goal_id == STATS_GOAL_ID)
    )

    with op.batch_alter_table("reviews") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(length=36), nullable=True))

    op.execute(
        """
        UPDATE reviews
        SET user_id = (
            SELECT client_ids.ident
            FROM client_ids
            WHERE client_ids.id = reviews.client_id
        )
        """
    )

    with op.batch_alter_table("reviews") as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.String(length=36), nullable=False)
        batch_op.create_foreign_key(
            "fk_reviews_user_id",
            "user_ids",
            ["user_id"],
            ["user_id"],
        )
        batch_op.drop_constraint("fk_reviews_client_id", type_="foreignkey")
        batch_op.drop_column("client_id")
