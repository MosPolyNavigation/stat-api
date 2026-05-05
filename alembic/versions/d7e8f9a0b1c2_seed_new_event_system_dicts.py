"""Заполнение справочников и связей новой системы событий

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
            {"id": 1, "name": "int", "description": "Целочисленное значение"},
            {"id": 2, "name": "string", "description": "Строковое значение"},
            {"id": 3, "name": "bool", "description": "Булево значение"},
        ],
    )

    op.bulk_insert(
        event_types,
        [
            {"id": 1, "code_name": "site", "description": "События сайта"},
            {"id": 2, "code_name": "auds", "description": "События выбора аудиторий"},
            {"id": 3, "code_name": "ways", "description": "События построения маршрутов"},
            {"id": 4, "code_name": "plans", "description": "События смены планов"},
        ],
    )

    # Решение по маппингу из бизнес-логики:
    # - endpoint/auditory_id/start_id/end_id/plan_id хранятся как строки.
    # - success хранится как bool.
    op.bulk_insert(
        payload_types,
        [
            {
                "id": 1,
                "code_name": "endpoint",
                "description": "Посещённый endpoint сайта",
                "value_type_id": 2,
            },
            {
                "id": 2,
                "code_name": "auditory_id",
                "description": "Идентификатор выбранной аудитории",
                "value_type_id": 2,
            },
            {
                "id": 3,
                "code_name": "start_id",
                "description": "Идентификатор начала маршрута",
                "value_type_id": 2,
            },
            {
                "id": 4,
                "code_name": "end_id",
                "description": "Идентификатор назначения маршрута",
                "value_type_id": 2,
            },
            {
                "id": 5,
                "code_name": "success",
                "description": "Флаг успешности операции",
                "value_type_id": 3,
            },
            {
                "id": 6,
                "code_name": "plan_id",
                "description": "Идентификатор выбранного плана",
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

    # payloads/events не очищаются явно.
    # Они удаляются каскадом FK при удалении строк справочников.
    op.execute("DELETE FROM payload_types WHERE id IN (1, 2, 3, 4, 5, 6)")
    op.execute("DELETE FROM event_types WHERE id IN (1, 2, 3, 4)")
    op.execute("DELETE FROM value_types WHERE id IN (1, 2, 3)")
