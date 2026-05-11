from pathlib import Path

import asyncio
import logging
import typer
from pydantic import PostgresDsn
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import Annotated

from app.config import load_settings
from app.models import (
    Problem, Goal, Right, Role, Floor, Location, Static, Type, ReviewStatus,
    ClientId, User, RefreshToken, UserLog, ValueType,
    EventType, Event, PayloadType, Payload, AllowedPayload,
    Corpus, Plan, Auditory, AudPhoto,
    RoleRightGoal, UserRole, Review,
    DodFloor, DodLocation, DodStatic, DodType,
    DodCorpus, DodPlan, DodAuditory, DodAudPhoto,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Порядок миграции — тот же, что в оригинальном скрипте
MIGRATION_ORDER = [
    ValueType, Problem, Goal, Right, Role, Floor, Location, Static, Type, ReviewStatus, User,
    ClientId, RefreshToken, UserLog, EventType, PayloadType,
    DodFloor, DodLocation, DodStatic, DodType,
    Corpus, Plan, Auditory, AudPhoto,
    RoleRightGoal, UserRole, Review,
    DodCorpus, DodPlan, DodAuditory, DodAudPhoto,
    Event, AllowedPayload, Payload,
]
CLEANUP_ORDER = list(reversed(MIGRATION_ORDER))


def get_pk_column(model) -> str | None:
    pk = model.__mapper__.primary_key
    return pk[0].name if len(pk) == 1 else None


def is_autoincrement_pk(model):
    pk = model.__mapper__.primary_key
    if len(pk) != 1:
        return False
    col = pk[0]
    return col.autoincrement and col.type.python_type is int


async def get_existing_ids(session: AsyncSession, model) -> set:
    pk = get_pk_column(model)
    if not pk:
        return set()
    stmt = select(getattr(model, pk))
    result = await session.execute(stmt)
    return {row[0] for row in result.all()}


async def update_sequence(session: AsyncSession, model):
    pk = get_pk_column(model)
    if not pk or not is_autoincrement_pk(model):
        return
    table = model.__tablename__
    seq_name = f"{table}_{pk}_seq"
    try:
        await session.execute(
            text(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX({pk}) FROM {table}), 1), true)")
        )
        await session.commit()
    except Exception as e:
        logger.warning(f"  ⚠ Не удалось обновить sequence для {table}: {e}")


async def clear_table(session: AsyncSession, model):
    table = model.__tablename__
    try:
        await session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
        await session.commit()
        logger.info(f"  ✓ Таблица {table} очищена")
    except Exception as e:
        logger.error(f"  ✗ Ошибка очистки {table}: {e}")
        await session.rollback()
        raise


async def clear_all_tables(session: AsyncSession):
    logger.info("🧹 Очистка всех таблиц PostgreSQL...")
    for model in CLEANUP_ORDER:
        try:
            await clear_table(session, model)
        except Exception as e:
            logger.error(f"✗ Не удалось очистить {model.__tablename__}: {e}")
            raise
    logger.info("✅ Очистка завершена")


async def migrate_model(session_sqlite: AsyncSession, session_pg: AsyncSession, model):
    logger.info(f"🔄 Миграция {model.__tablename__}...")

    result = await session_sqlite.execute(select(model))
    sqlite_objs = result.scalars().all()
    if not sqlite_objs:
        logger.info("  ℹ Нет данных в SQLite")
        return

    existing_pks = await get_existing_ids(session_pg, model)
    pk_attr = get_pk_column(model)

    new_objects = []
    for obj in sqlite_objs:
        if pk_attr:
            pk_value = getattr(obj, pk_attr)
            if pk_value in existing_pks:
                continue
        data = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
        new_obj = model(**data)
        new_objects.append(new_obj)

    if not new_objects:
        logger.info("  ℹ Все записи уже существуют")
        return

    batch_size = 500
    total = len(new_objects)

    for i in range(0, total, batch_size):
        batch = new_objects[i:i + batch_size]
        session_pg.add_all(batch)
        await session_pg.commit()
        logger.info("  ✓ Вставлено {len(batch)}/{total} записей")

    await update_sequence(session_pg, model)
    logger.info(f"✅ {model.__tablename__} мигрирована")


async def _run_migration(sqlite_dsn: str, pg_dsn: str, clean_before: bool):
    """Внутренняя логика: создание движков и запуск миграции."""
    sqlite_engine = create_async_engine(sqlite_dsn, future=True)
    pg_engine = create_async_engine(pg_dsn, future=True)

    sqlite_session = async_sessionmaker(sqlite_engine, expire_on_commit=False)
    pg_session = async_sessionmaker(pg_engine, expire_on_commit=False)

    try:
        async with sqlite_session() as session_sqlite, pg_session() as session_pg:
            if clean_before:
                await clear_all_tables(session_pg)

            for model in MIGRATION_ORDER:
                try:
                    await migrate_model(session_sqlite, session_pg, model)
                except Exception as e:
                    logger.error(f"Ошибка при миграции {model.__tablename__}: {e}")
                    await session_pg.rollback()
                    raise
    finally:
        await sqlite_engine.dispose()
        await pg_engine.dispose()


# ── Typer-команда ──────────────────────────────────────────────────────

def sqlite_to_pg_command(
    sqlite_path: Annotated[
        Path,
        typer.Argument(..., help="Путь к файлу SQLite-базы (например, app.db)"),
    ],
    clean: Annotated[
        bool,
        typer.Option("--clean", help="Очистить целевую БД перед миграцией"),
    ] = True,
    pg_dsn_override: Annotated[
        str | None,
        typer.Option("--pg-dsn", help="Переопределить PostgreSQL DSN из конфига"),
    ] = None,
) -> None:
    """
    Миграция данных из SQLite в PostgreSQL.
    PostgreSQL-строка подключения берётся из конфига (переменная STATAPI_CONFIG).
    """
    # 1. Загружаем конфиг
    settings = load_settings()

    # 2. Получаем и валидируем PostgreSQL DSN
    pg_dsn = pg_dsn_override or str(settings.sqlalchemy_database_url)
    try:
        # Валидация через Pydantic PostgresDsn
        PostgresDsn(pg_dsn)
    except Exception as e:
        typer.echo(f"❌ Некорректный PostgreSQL DSN: {e}")
        raise typer.Exit(1)

    # 3. Формируем SQLite DSN из аргумента
    sqlite_dsn = f"sqlite+aiosqlite:///{sqlite_path.resolve()}"
    if not sqlite_path.exists():
        typer.echo(f"❌ Файл не найден: {sqlite_path}")
        raise typer.Exit(1)

    typer.echo(f"🔌 SQLite: {sqlite_dsn}")
    typer.echo(f"🔌 PostgreSQL: {pg_dsn}")
    typer.echo(f"🧹 Очистка перед миграцией: {clean}")

    # 4. Запускаем асинхронную миграцию
    try:
        asyncio.run(_run_migration(sqlite_dsn, pg_dsn, clean_before=clean))
        typer.echo("✅ Миграция завершена успешно")
    except Exception as e:
        typer.echo(f"💥 Ошибка миграции: {e}")
        raise typer.Exit(1)
