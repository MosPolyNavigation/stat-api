import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypedDict

from fastapi import FastAPI

from app.config import get_settings
from app.guards.governor import stat_rate_limiter
from app.guards.review_governor import review_rate_limiter
from app.jobs.governor_cleaner.stat_cleaner import create_cleanup_job
from app.jobs.manager import JobManager
from app.jobs.models.job_config import JobsConfig
from app.jobs.refresh_token import delete_old_refresh_tokens, revoke_expired_refresh_tokens

# Импорт задач, чтобы @scheduled_task отработал при старте и заполнил реестр
from app.jobs.location_data.worker import fetch_location_data  # noqa: F401
from app.jobs.rasp import fetch_cur_rasp  # noqa: F401

logger = logging.getLogger(__name__)

STAT_LIMITERS = [stat_rate_limiter]


class AppLifespanState(TypedDict):
    job_manager: JobManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[AppLifespanState, None]:
    settings = get_settings()

    # Загрузка банов перед стартом
    try:
        loaded = review_rate_limiter.load_bans(app.state, settings)
        if loaded > 0:
            logger.info("Loaded %d banned users from %s", loaded, settings.static_files)
    except Exception as e:
        logger.warning("Could not load banned users: %s", e)

    # Создаём JobManager из конфига
    jobs_config_data = getattr(settings, "jobs", None)
    if jobs_config_data is None:
        jobs_config = JobsConfig()
    elif isinstance(jobs_config_data, JobsConfig):
        jobs_config = jobs_config_data
    else:
        jobs_config = JobsConfig.model_validate(jobs_config_data)

    job_manager = JobManager(
        static_path=settings.static_files,
        queue_type=jobs_config.queue,
        queue_db=jobs_config.url,
    )
    job_manager.setup_from_config(jobs_config)

    # Системные задачи (не входят в публичный реестр @scheduled_task)
    job_manager.add_job(
        create_cleanup_job(app, STAT_LIMITERS),
        trigger="interval",
        minutes=5,
        id="rate_limiter_cleanup",
        name="Clean up expired rate limiter entries",
        replace_existing=True,
    )
    job_manager.add_job(
        create_cleanup_job(app, [review_rate_limiter]),
        trigger="interval",
        minutes=10,
        id="review_rate_limiter_cleanup",
        name="Clean up review rate limiter entries",
        replace_existing=True,
    )
    job_manager.add_job(
        revoke_expired_refresh_tokens,
        trigger="interval",
        minutes=5,
        id="refresh_token_auto_revoke",
        name="Auto revoke expired refresh tokens",
        replace_existing=True,
        max_instances=1,
    )
    job_manager.add_job(
        delete_old_refresh_tokens,
        trigger="cron",
        hour=22,
        minute=49,
        id="refresh_token_daily_cleanup",
        name="Delete old refresh tokens",
        replace_existing=True,
        max_instances=1,
    )

    await job_manager.start()

    # Первоначальная загрузка данных локаций
    await fetch_location_data()

    # Передаём job_manager в request.state через lifespan state
    yield AppLifespanState(job_manager=job_manager)

    # Сохранение банов перед выключением
    try:
        saved = review_rate_limiter.save_bans(app.state, settings)
        if saved:
            logger.info("Saved banned users to %s", settings.static_files)
        else:
            logger.warning("Failed to save banned users")
    except Exception as e:
        logger.error("Error saving banned users: %s", e)

    job_manager.shutdown()
