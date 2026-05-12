# app/helpers/seeding.py
import logging
from typing import Sequence, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

if TYPE_CHECKING:
    from app.seed.base_seeder import BaseSeeder

logger = logging.getLogger(__name__)


async def apply_seeding(
    seeders: Sequence["BaseSeeder"],
    session_maker: async_sessionmaker[AsyncSession] | None = None,
) -> None:
    """
    Применяет сидеры к базе данных.

    Args:
        seeders: Список экземпляров сидеров (наследников BaseSeeder).
        session_maker: Опциональный session_maker. Если не передан,
                       используется глобальный get_session_maker().

    Note:
        Все сидеры выполняются в одной транзакции. Если один упадёт —
        изменения откатятся. Для изоляции каждого сидера вызывайте
        эту функцию отдельно для каждого.
    """
    if not seeders:
        logger.debug("🌱 No seeders to apply")
        return

    # Ленивый импорт, чтобы избежать циклических зависимостей
    if session_maker is None:
        from app.database import get_session_maker
        session_maker = get_session_maker()

    logger.info("🌱 Applying database seeders...")
    
    async with session_maker() as session:
        for seeder in seeders:
            await seeder.add_missing(session)
            logger.debug(f"  ↳ {seeder.model.__name__} processed")
        await session.commit()
    
    logger.info("✅ Database seeded successfully.")


async def apply_seeding_isolated(
    seeders: Sequence["BaseSeeder"],
    session_maker: async_sessionmaker[AsyncSession] | None = None,
) -> None:
    """
    Применяет сидеры, каждый в отдельной транзакции.

    Полезно, когда нужно, чтобы успешные сидеры не откатывались
    при ошибке в последующих.
    """
    if session_maker is None:
        from app.database import get_session_maker
        session_maker = get_session_maker()

    for seeder in seeders:
        async with session_maker() as session:
            await seeder.add_missing(session)
            await session.commit()
        logger.debug(f"✅ {seeder.model.__name__} seeded (isolated)")


async def rollback_seeding(
    seeders: Sequence["BaseSeeder"],
    session_maker: async_sessionmaker[AsyncSession] | None = None,
) -> None:
    """
    Откатывает данные, добавленные сидерами (в одной транзакции).
    ⚠️ Итерация идёт в ОБРАТНОМ порядке, чтобы избежать FK-violations.
    """
    if not seeders:
        return
    if session_maker is None:
        from app.database import get_session_maker
        session_maker = get_session_maker()

    logger.info("🔄 Rolling back database seeders...")
    async with session_maker() as session:
        for seeder in reversed(seeders):
            await seeder.remove_present(session)
        await session.commit()
    logger.info("✅ Database rollback completed.")


async def rollback_seeding_isolated(
    seeders: Sequence["BaseSeeder"],
    session_maker: async_sessionmaker[AsyncSession] | None = None,
) -> None:
    """
    Откатывает данные сидеров по одному.
    Полезно для пошаговой отладки или когда нужно сохранить частично успешный откат.
    """
    if not seeders:
        return
    if session_maker is None:
        from app.database import get_session_maker
        session_maker = get_session_maker()

    logger.info("🔄 Rolling back database seeders (isolated)...")
    for seeder in reversed(seeders):
        async with session_maker() as session:
            await seeder.remove_present(session)
            await session.commit()
        logger.debug(f"🗑️ {seeder.model.__name__} rolled back")
