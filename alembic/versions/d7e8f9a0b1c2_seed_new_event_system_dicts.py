"""Seed new event system dictionaries and relations

Revision ID: d7e8f9a0b1c2
Revises: c1a2f3e4d5b6
Create Date: 2026-04-15 21:35:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7e8f9a0b1c2"
down_revision: Union[str, None] = "c1a2f3e4d5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    value_types = sa.sql.table(
        "value_types",
        sa.sql.column("id", sa.Integer),
        sa.sql.column("name", sa.String(length=20)),
        sa.sql.column("description", sa.String(length=100)),
    )
    event_types = sa.sql.table(
        "event_types",
        sa.sql.column("id", sa.Integer),
        sa.sql.column("code_name", sa.String(length=20)),
        sa.sql.column("description", sa.String(length=100)),
    )
    payload_types = sa.sql.table(
        "payload_types",
        sa.sql.column("id", sa.Integer),
        sa.sql.column("code_name", sa.String(length=20)),
        sa.sql.column("description", sa.String(length=100)),
        sa.sql.column("value_type_id", sa.Integer),
    )
    allowed_payloads = sa.sql.table(
        "allowed_payloads",
        sa.sql.column("event_type_id", sa.Integer),
        sa.sql.column("payload_type_id", sa.Integer),
    )

    op.bulk_insert(
        value_types,
        [
            {"id": 1, "name": "int", "description": "Integer value"},
            {"id": 2, "name": "string", "description": "String value"},
            {"id": 3, "name": "bool", "description": "Boolean value"},
        ],
    )

    op.bulk_insert(
        event_types,
        [
            {"id": 1, "code_name": "site", "description": "Site events"},
            {"id": 2, "code_name": "auds", "description": "Auditory selection events"},
            {"id": 3, "code_name": "ways", "description": "Route build events"},
            {"id": 4, "code_name": "plans", "description": "Plan change events"},
        ],
    )

    # Mapping decision (business-logic assumption):
    # - endpoint/auditory_id/start_id/end_id/plan_id are stored as strings.
    # - success is stored as bool.
    op.bulk_insert(
        payload_types,
        [
            {
                "id": 1,
                "code_name": "endpoint",
                "description": "Visited site endpoint",
                "value_type_id": 2,
            },
            {
                "id": 2,
                "code_name": "auditory_id",
                "description": "Selected auditory identifier",
                "value_type_id": 2,
            },
            {
                "id": 3,
                "code_name": "start_id",
                "description": "Route start identifier",
                "value_type_id": 2,
            },
            {
                "id": 4,
                "code_name": "end_id",
                "description": "Route destination identifier",
                "value_type_id": 2,
            },
            {
                "id": 5,
                "code_name": "success",
                "description": "Operation success flag",
                "value_type_id": 3,
            },
            {
                "id": 6,
                "code_name": "plan_id",
                "description": "Selected plan identifier",
                "value_type_id": 2,
            },
        ],
    )

    op.bulk_insert(
        allowed_payloads,
        [
            {"event_type_id": 1, "payload_type_id": 1},
            {"event_type_id": 2, "payload_type_id": 2},
            {"event_type_id": 2, "payload_type_id": 5},
            {"event_type_id": 3, "payload_type_id": 3},
            {"event_type_id": 3, "payload_type_id": 4},
            {"event_type_id": 3, "payload_type_id": 5},
            {"event_type_id": 4, "payload_type_id": 6},
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM allowed_payloads WHERE event_type_id IN (1, 2, 3, 4) AND payload_type_id IN (1, 2, 3, 4, 5, 6)"
    )

    # payloads/events are not cleaned explicitly.
    # they are removed by FK cascades from deleted dictionary rows.
    op.execute("DELETE FROM payload_types WHERE id IN (1, 2, 3, 4, 5, 6)")
    op.execute("DELETE FROM event_types WHERE id IN (1, 2, 3, 4)")
    op.execute("DELETE FROM value_types WHERE id IN (1, 2, 3)")
