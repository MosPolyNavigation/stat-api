import logging
from functools import partial
from os import makedirs, path
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from sqlalchemy.exc import SQLAlchemyError

from app.config import JobsConfig, Settings
from app.database import close_database, init_database
from app.guards.governor import stat_rate_limiter
from app.guards.review_governor import review_rate_limiter
from app.helpers.errors import LookupException
from app.helpers.spa_static_files import SPAStaticFiles
from app.hooks import BaseHooks
from app.jobs import AppLifespanState
from app.jobs.governor_cleaner.stat_cleaner import create_cleanup_job
from app.jobs.location_data.worker import fetch_location_data
from app.jobs.manager import JobManager
from app.jobs.refresh_token import (
    delete_old_refresh_tokens,
    revoke_expired_refresh_tokens,
)
from app.routes import (
    admin,
    auth,
    check,
    free_aud,
    get,
    graphql,
    jobs,
    nav,
    review,
    stat,
)
from app.state import AppState

logger = logging.getLogger(__name__)


TAGS_METADATA = [
    {"name": "stat", "description": "Эндпоинты для внесения статистики"},
    {"name": "get", "description": "Эндпоинты для получения статистики"},
    {"name": "review", "description": "Эндпоинты для работы с отзывами"},
    {"name": "graphql", "description": "Эндпоинт для запросов graphql"},
    {"name": "auth", "description": "Эндпоинты для аутентификации и авторизации"},
    {"name": "jobs", "description": "Эндпоинты для управления фоновыми задачами"},
    {"name": "free-aud", "description": "Эндпоинты для получения свободных аудиторий"},
    {"name": "nav", "description": "Эндпоинты для работы с данными навигации"},
    {"name": "check", "description": "Эндпоинты для проверки"},
    {"name": "admin", "description": "Эндпоинты для управления забаненными пользователями"},
]

APP_VERSION = "0.2.1"

# Cleanup-задачи лимитеров вынесены в константу, чтобы не плодить захваченных ссылок в замыканиях.
STAT_LIMITERS = [stat_rate_limiter]


class DefaultHooks(BaseHooks):
    """
    Хуки по умолчанию: воспроизводят прежнее поведение app/app.py + lifespan
    из app/jobs/__init__.py через сегментированный API.
    """

    # ── Сегменты конфигурации ────────────────────────────────────────────────

    def setup_middlewares(self, app: FastAPI, settings: Settings) -> None:
        # Поля, которые нельзя задать во фабрике без расширения её сигнатуры,
        # ставим прямо здесь — это ближе всего к моменту создания FastAPI.
        app.version = APP_VERSION
        app.openapi_tags = TAGS_METADATA

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_hosts,
            allow_methods=settings.allowed_methods,
            allow_headers=settings.allowed_headers,
            allow_credentials=settings.allow_credentials,
        )
        app.add_middleware(GZipMiddleware, minimum_size=1024)
        add_pagination(app)

    def setup_routers(self, app: FastAPI) -> None:
        # Состояние привязано к приложению ДО роутеров: guard-зависимости
        # читают его в момент обработки запроса, и оно должно быть на месте.
        app.state.app_state = AppState()

        app.include_router(get.router)
        app.include_router(stat.router)
        app.include_router(review.router)
        app.include_router(check.router)
        app.include_router(auth.router)
        app.include_router(graphql.graphql_router, prefix="/api/graphql", tags=["graphql"])
        app.include_router(jobs.router)
        app.include_router(free_aud.router)
        app.include_router(nav.router)
        app.include_router(admin.router)

    def setup_static_files(self, app: FastAPI, settings: Settings) -> None:
        current_file_dir = path.dirname(path.abspath(__file__))
        project_dir = path.dirname(current_file_dir)
        admin_dir = path.join(project_dir, "dist-panel")

        directories: List[str] = [
            path.join(settings.static_files, "images"),
            path.join(settings.static_files, "auditories"),
            path.join(settings.static_files, "plans"),
            path.join(settings.static_files, "thumbnails"),
            admin_dir,
        ]
        for directory in directories:
            if not path.exists(directory):
                makedirs(directory)

        app.mount(
            "/admin/",
            SPAStaticFiles(directory=admin_dir, html=True),
            "admin",
        )

    def setup_exception_handlers(self, app: FastAPI) -> None:
        @app.exception_handler(SQLAlchemyError)
        async def sqlalchemy_exception_handler(_, exc: SQLAlchemyError):
            return JSONResponse(status_code=500, content={"status": str(exc)})

        @app.exception_handler(LookupException)
        async def lookup_exception_handler(_, exc: LookupException):
            return JSONResponse(status_code=404, content={"status": str(exc)})

        @app.exception_handler(HTTPException)
        async def http_exception_handler(_: Request, exc: HTTPException):
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    # ── Lifespan ─────────────────────────────────────────────────────────────

    async def on_startup(self, app: FastAPI, settings: Settings) -> AppLifespanState:
        init_database(settings)

        state: AppState = app.state.app_state

        try:
            loaded = review_rate_limiter.load_bans(state, settings)
            if loaded > 0:
                logger.info("Loaded %d banned users from %s", loaded, settings.static_files)
        except Exception as e:
            logger.warning("Could not load banned users: %s", e)

        jobs_config = self._resolve_jobs_config(settings)

        job_manager = JobManager(
            static_path=settings.static_files,
            queue_type=jobs_config.queue,
            queue_db=jobs_config.url,
        )
        job_manager.setup_from_config(jobs_config)

        # setup_from_config зарегистрировал воркеры из реестра @scheduled_task,
        # но без аргументов. Пере-регистрируем их через partial(state=state) —
        # replace_existing=True заменит запись в APScheduler. Расписание берём
        # из YAML, чтобы не дублировать его в коде.
        self._reschedule_with_state(job_manager, jobs_config, state)

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

        # Первоначальная загрузка locationData в state — чтобы первый запрос
        # уже видел готовые данные, не дожидаясь триггера планировщика.
        await fetch_location_data(state=state)

        return AppLifespanState(job_manager=job_manager)

    async def on_shutdown(
        self,
        app: FastAPI,
        settings: Settings,
        state: AppLifespanState,
    ) -> None:
        try:
            saved = review_rate_limiter.save_bans(app.state.app_state, settings)
            if saved:
                logger.info("Saved banned users to %s", settings.static_files)
            else:
                logger.warning("Failed to save banned users")
        except Exception as e:
            logger.error("Error saving banned users: %s", e)

        state["job_manager"].shutdown()
        await close_database()

    # ── Внутреннее ───────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_jobs_config(settings: Settings) -> JobsConfig:
        jobs_config_data = getattr(settings, "jobs", None)
        if jobs_config_data is None:
            return JobsConfig()
        if isinstance(jobs_config_data, JobsConfig):
            return jobs_config_data
        return JobsConfig.model_validate(jobs_config_data)

    @staticmethod
    def _reschedule_with_state(
        job_manager: JobManager,
        jobs_config: JobsConfig,
        state: AppState,
    ) -> None:
        """
        Переопределяет регистрации воркеров, требующих AppState.

        setup_from_config регистрирует чистый wrapper из @scheduled_task (без
        аргументов), но воркеры fetch_location_data / fetch_cur_rasp требуют
        state. Делаем повторный add_job с partial(state=...) и replace_existing=True
        — APScheduler заменит запись по тому же id. Триггеры берутся из YAML-конфига.
        """
        from app.jobs.manager import get_task_registry  # локальный импорт во избежание циклов

        registry_by_name = {entry["name"]: entry for entry in get_task_registry()}
        stateful_names = {"fetch_location_data", "fetch_cur_rasp"}

        for job_cfg in jobs_config.tasks:
            if not job_cfg.enabled or job_cfg.name not in stateful_names:
                continue

            entry = registry_by_name.get(job_cfg.name)
            if entry is None:
                logger.warning(
                    "Stateful worker '%s' is in config but not in @scheduled_task registry",
                    job_cfg.name,
                )
                continue

            wrapped = partial(entry["func"], state=state)
            kwargs = JobManager._build_apscheduler_kwargs(job_cfg)
            kwargs["replace_existing"] = True
            job_manager.add_job(wrapped, **kwargs)
