from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings

engine = create_async_engine(str(get_settings().sqlalchemy_database_url), future=True)
AsyncSessionLocal = async_sessionmaker(autoflush=True, autocommit=False, bind=engine, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция для получения сессии базы данных.

    Эта функция создает сессию базы данных и возвращает ее.
    После использования сессии она закрывается.

    Yields:
        Session: Сессия базы данных.
    """
    async with AsyncSessionLocal() as db:
        yield db
