from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.guards.governor import stat_rate_limiter
from app.jobs.rasp import fetch_cur_rasp
from app.jobs.schedule.schedule import fetch_cur_data
from app.jobs.location_data.worker import fetch_location_data
from app.jobs.governor_cleaner.stat_cleaner import create_cleanup_job 

STAT_LIMITERS = [
    stat_rate_limiter
]
#
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
    # scheduler.add_job(fetch_cur_data, "interval", minutes=10)
    scheduler.add_job(fetch_location_data, "interval", hours=1)
    scheduler.add_job(fetch_cur_rasp, "cron", hour=0, minute=0)
    scheduler.add_job(
        create_cleanup_job(app, STAT_LIMITERS),
        trigger="interval",
        minutes=5,
        id="rate_limiter_cleanup",
        name="Clean up expired rate limiter entries",
        replace_existing=True,
    )

    await fetch_location_data()

    scheduler.start()

    yield

    scheduler.shutdown(wait=True)
    
    # Опционально: финальная очистка перед выходом
    for limiter in STAT_LIMITERS:
        limiter.cleanup_now(app.state)
