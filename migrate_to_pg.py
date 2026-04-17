import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, text
import logging

from app.models import (
    UserId, Problem, Goal, Right, Role, Floor, Location, Static, Type, ReviewStatus,
    TgEventType, User, TgUser,
    Corpus, Plan, Auditory, AudPhoto,
    RoleRightGoal, UserRole, Review,
    SelectAuditory, SiteStat, StartWay, ChangePlan, TgEvent,
    DodFloor, DodLocation, DodStatic, DodType, DodCorpus, DodPlan, DodAuditory, DodAudPhoto,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLITE_DSN = "sqlite+aiosqlite:///database.db"
POSTGRES_DSN = "postgresql+asyncpg://user:pass@localhost:5432/database"

sqlite_engine = create_async_engine(SQLITE_DSN, future=True)
pg_engine = create_async_engine(POSTGRES_DSN, future=True)

SqliteSession = async_sessionmaker(sqlite_engine, expire_on_commit=False)
PgSession = async_sessionmaker(pg_engine, expire_on_commit=False)

MIGRATION_ORDER = [
    UserId, Problem, Goal, Right, Role, Floor, Location, Static, Type,
    ReviewStatus, TgEventType, User, TgUser,
    DodFloor, DodLocation, DodStatic, DodType,
    Corpus, Plan, Auditory, AudPhoto,
    RoleRightGoal, UserRole, Review,
    SelectAuditory, SiteStat, StartWay, ChangePlan, TgEvent,
    DodCorpus, DodPlan, DodAuditory, DodAudPhoto,
]

CLEANUP_ORDER = list(reversed(MIGRATION_ORDER))

def get_pk_column(model):
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
        await session.execute(text(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX({pk}) FROM {table}), 1), true)"))
        await session.commit()
    except Exception as e:
        logger.warning(f"  Не удалось обновить sequence для {table}: {e}")

async def clear_table(session: AsyncSession, model):
    """Очистить таблицу в PostgreSQL."""
    table = model.__tablename__
    try:
        # TRUNCATE ... CASCADE удалит все связанные записи
        await session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
        await session.commit()
        logger.info(f"  Таблица {table} очищена")
    except Exception as e:
        logger.error(f"  Ошибка очистки {table}: {e}")
        await session.rollback()
        raise

async def clear_all_tables(session: AsyncSession):
    """Очистить все таблицы в правильном порядке (сначала дочерние)."""
    logger.info("Очистка всех таблиц PostgreSQL...")
    for model in CLEANUP_ORDER:
        try:
            await clear_table(session, model)
        except Exception as e:
            logger.error(f"Не удалось очистить {model.__tablename__}: {e}")
            raise
    logger.info("Очистка завершена")

async def migrate_model(session_sqlite: AsyncSession, session_pg: AsyncSession, model):
    logger.info(f"Миграция {model.__tablename__}...")

    # 1. Получаем все записи из SQLite
    result = await session_sqlite.execute(select(model))
    sqlite_objs = result.scalars().all()
    if not sqlite_objs:
        logger.info(f"  Нет данных в SQLite")
        return

    # 2. (Опционально) можно пропустить проверку существующих записей,
    #    т.к. таблица уже очищена. Но оставим для гибкости.
    existing_pks = await get_existing_ids(session_pg, model)
    pk_attr = get_pk_column(model)

    # 3. Создаём новые объекты для вставки (не привязанные к сессии)
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
        logger.info(f"  Все записи уже существуют (после очистки такого быть не должно)")
        return

    # 4. Вставляем пачками
    batch_size = 500
    for i in range(0, len(new_objects), batch_size):
        batch = new_objects[i:i+batch_size]
        session_pg.add_all(batch)
        await session_pg.commit()
        logger.info(f"  Вставлено {len(batch)} записей (всего новых {len(new_objects)})")

    # 5. Обновляем sequence
    await update_sequence(session_pg, model)

async def main(clean_before_migrate: bool = True):
    async with SqliteSession() as session_sqlite, PgSession() as session_pg:
        if clean_before_migrate:
            await clear_all_tables(session_pg)

        for model in MIGRATION_ORDER:
            try:
                await migrate_model(session_sqlite, session_pg, model)
            except Exception as e:
                logger.error(f"Ошибка при миграции {model.__tablename__}: {e}")
                await session_pg.rollback()

if __name__ == "__main__":
    # Установите clean_before_migrate=False, если не хотите очищать
    asyncio.run(main(clean_before_migrate=True))
