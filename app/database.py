"""Подключение к базе данных и фабрика сессий SQLAlchemy."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

engine = create_async_engine(str(get_settings().sqlalchemy_database_url), future=True)
AsyncSessionLocal = async_sessionmaker(autoflush=True, autocommit=False, bind=engine, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Провайдер асинхронной сессии БД для зависимостей FastAPI.

    Создает сессию, возвращает её через `yield` и корректно закрывает после использования.
    """
    async with AsyncSessionLocal() as db:
        yield db
