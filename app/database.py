from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Settings

# Модульное состояние подключения к БД.
# Engine и session_maker создаются явно через init_database() из lifespan,
# а не на уровне модуля — это убирает сайд-эффект при `import app`
# и позволяет тестам подменять источник сессий без патчинга sys.modules.
_engine: Optional[AsyncEngine] = None
_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def init_database(settings: Settings) -> None:
    """Создаёт engine и session_maker из настроек. Вызывается в on_startup хука."""
    global _engine, _session_maker
    _engine = create_async_engine(str(settings.sqlalchemy_database_url), future=True)
    _session_maker = async_sessionmaker(
        autoflush=True,
        autocommit=False,
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def close_database() -> None:
    """Закрывает engine и сбрасывает модульные переменные. Вызывается в on_shutdown."""
    global _engine, _session_maker
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_maker = None


def override_database(session_maker: async_sessionmaker[AsyncSession]) -> None:
    """Подменяет session_maker. Используется только в тестах для подключения тестовой БД."""
    global _session_maker
    _session_maker = session_maker


def reset_database() -> None:
    """Сбрасывает модульное состояние без вызова dispose. Используется в тестах."""
    global _engine, _session_maker
    _engine = None
    _session_maker = None


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Возвращает текущий session_maker или бросает RuntimeError, если БД ещё не инициализирована."""
    if _session_maker is None:
        raise RuntimeError(
            "Database is not initialized. "
            "Call init_database(settings) in lifespan before using sessions."
        )
    return _session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI-зависимость для получения сессии БД.

    Yields:
        AsyncSession: открытая сессия, автоматически закрывается после запроса.
    """
    session_maker = get_session_maker()
    async with session_maker() as db:
        yield db
