"""Настройка фоновых задач (lifespan) для обновления данных."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.jobs.rasp import fetch_cur_rasp
from app.jobs.schedule.schedule import fetch_cur_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Контекст жизненного цикла приложения: запускает планировщик фоновых задач.

    Args:
        _: Экземпляр FastAPI, передаваемый фреймворком (не используется напрямую).

    Yields:
        None: После запуска задач передает управление FastAPI, затем останавливает планировщик.
    """
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
    scheduler.add_job(fetch_cur_data, "interval", minutes=10)
    scheduler.add_job(fetch_cur_rasp, "cron", hour=0, minute=0)
    await fetch_cur_data()
    # await fetch_cur_rasp()
    scheduler.start()
    yield
    scheduler.shutdown()
