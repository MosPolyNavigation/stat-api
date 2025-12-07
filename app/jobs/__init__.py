"""Инициализация фоновых задач и lifespan-хука приложения."""

from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.jobs.rasp import fetch_cur_rasp
from app.jobs.schedule.schedule import fetch_cur_data

__all__ = ["lifespan", "fetch_cur_rasp"]


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Запускает планировщик APScheduler при старте приложения и останавливает при завершении.

    - fetch_cur_data каждые 10 минут обновляет навигационные данные
    - fetch_cur_rasp раз в сутки обновляет расписание
    """
    scheduler = AsyncIOScheduler({"apscheduler.timezone": "Europe/Moscow"})
    scheduler.add_job(fetch_cur_data, "interval", minutes=10)
    scheduler.add_job(fetch_cur_rasp, "cron", hour=0, minute=0)
    await fetch_cur_data()
    scheduler.start()
    yield
    scheduler.shutdown()
