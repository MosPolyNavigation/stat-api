"""Создание подключения SQLAlchemy и вспомогательная выдача сессий."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings

engine = create_async_engine(str(get_settings().sqlalchemy_database_url), future=True)
AsyncSessionLocal = async_sessionmaker(autoflush=True, autocommit=False, bind=engine, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Провайдер сессии базы данных для зависимостей FastAPI.

    Args:
        None

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy, корректно закрываемая после использования.
    """
    async with AsyncSessionLocal() as db:
        yield db
