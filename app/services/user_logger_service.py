import asyncio
import os
from typing import Optional, AsyncGenerator

from fastapi import Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.database import get_db
from app.models import User, UserLog


# Сохраняет запись лога в БД и выполняет откат транзакции при ошибке
async def background_log(db_session: AsyncSession, log_record: UserLog) -> None:
    try:
        db_session.add(log_record)
        await db_session.commit()
    except Exception:
        await db_session.rollback()


class UserLoggerService:
    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ):
        self._session = db_session
        self._background_tasks = background_tasks
        self._session_factory = get_db

    # Создаёт независимую сессию БД для фонового логирования
    async def get_background_session(
        self,
    ) -> tuple[AsyncSession, Optional[AsyncGenerator]]:
        if self._session is not None and self._session.bind is not None:
            session_factory = async_sessionmaker(
                bind=self._session.bind,
                class_=AsyncSession,
                autoflush=True,
                autocommit=False,
                expire_on_commit=False,
            )
            return session_factory(), None

        db_generator = self._session_factory()
        db_session = await anext(db_generator)
        return db_session, db_generator

    # Формирует запись лога и сохраняет её в БД через отдельную сессию
    async def background_log(self, user: User, text: str) -> None:
        db_session = None
        db_generator = None

        try:
            db_session, db_generator = await self.get_background_session()
            log_record = UserLog(
                user_id=user.id,
                text=f"Пользователь с логином {user.login} выполнил следующее действие: {text}",
            )
            await background_log(db_session, log_record)
        except Exception:
            pass
        finally:
            if db_generator is not None:
                await db_generator.aclose()
            elif db_session is not None:
                await db_session.close()

    # Запускает фоновую запись пользовательского действия, если логирование включено
    def log(self, user: Optional[User], text: str):
        if os.getenv("STATAPI_LOGGING", "1") == "0":
            return None

        if user is None:
            return None

        if self._background_tasks is not None:
            self._background_tasks.add_task(self.background_log, user, text)
            return None

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.background_log(user, text))
        except RuntimeError:
            return None
        except Exception:
            return None

        return None

    async def log_now(self, user: Optional[User], text: str):
        if os.getenv("STATAPI_LOGGING", "1") == "0":
            return None

        if user is None:
            return None

        await self.background_log(user, text)
        return None


def get_user_logger_service(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> UserLoggerService:
    return UserLoggerService(db, background_tasks)
