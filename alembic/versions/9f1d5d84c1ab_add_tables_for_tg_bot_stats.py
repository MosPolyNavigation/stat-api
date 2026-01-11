"""Добавляет таблицы статистики телеграм-бота

Revision ID: 9f1d5d84c1ab
Revises: e50b31c48695
Create Date: 2026-01-11 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f1d5d84c1ab'
down_revision: Union[str, None] = 'e50b31c48695'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tg_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tg_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tg_id')
    )
    op.create_index(op.f('ix_tg_users_id'), 'tg_users', ['id'], unique=False)
    op.create_index(op.f('ix_tg_users_tg_id'), 'tg_users', ['tg_id'], unique=False)

    op.create_table(
        'tg_event_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tg_event_types_id'), 'tg_event_types', ['id'], unique=False)
    op.create_index(op.f('ix_tg_event_types_name'), 'tg_event_types', ['name'], unique=False)

    op.create_table(
        'tg_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('time', sa.DateTime(), nullable=False),
        sa.Column('tg_id', sa.Integer(), nullable=False),
        sa.Column('event_type_id', sa.Integer(), nullable=False),
        sa.Column('is_dod', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['event_type_id'], ['tg_event_types.id'], ),
        sa.ForeignKeyConstraint(['tg_id'], ['tg_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tg_events_event_type_id'), 'tg_events', ['event_type_id'], unique=False)
    op.create_index(op.f('ix_tg_events_id'), 'tg_events', ['id'], unique=False)
    op.create_index(op.f('ix_tg_events_time'), 'tg_events', ['time'], unique=False)
    op.create_index(op.f('ix_tg_events_tg_id'), 'tg_events', ['tg_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tg_events_tg_id'), table_name='tg_events')
    op.drop_index(op.f('ix_tg_events_time'), table_name='tg_events')
    op.drop_index(op.f('ix_tg_events_id'), table_name='tg_events')
    op.drop_index(op.f('ix_tg_events_event_type_id'), table_name='tg_events')
    op.drop_table('tg_events')
    op.drop_index(op.f('ix_tg_event_types_name'), table_name='tg_event_types')
    op.drop_index(op.f('ix_tg_event_types_id'), table_name='tg_event_types')
    op.drop_table('tg_event_types')
    op.drop_index(op.f('ix_tg_users_tg_id'), table_name='tg_users')
    op.drop_index(op.f('ix_tg_users_id'), table_name='tg_users')
    op.drop_table('tg_users')
