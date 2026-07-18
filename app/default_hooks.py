import logging
from os import makedirs, path
from pathlib import Path
from typing import List, Any, LiteralString

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
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
from app.graphql.schema import graphql_router
from app.routes import (
    admin,
    auth,
    check,
    free_aud,
    get,
    jobs,
    nav,
    review,
    stat,
)
from app.state import AppState
from app.seed.base_seeder import BaseSeeder

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
    {
        "name": "admin",
        "description": "Эндпоинты для управления забаненными пользователями",
    },
]

APP_VERSION = "0.4.1"

# Cleanup-задачи лимитеров вынесены в константу, чтобы не плодить захваченных ссылок в замыканиях.
STAT_LIMITERS = [stat_rate_limiter]


class DefaultHooks(BaseHooks):
    """
    Хуки по умолчанию: воспроизводят прежнее поведение app/app.py + lifespan
    из app/jobs/__init__.py через сегментированный API.
    """

    def setup_seeders(self) -> list[BaseSeeder]:
        from app.seed import (
            AllowedPayloadSeeder,
            DashboardTypeSeeder,
            EventTypeSeeder,
            FloorSeeder,
            GoalSeeder,
            PayloadTypeSeeder,
            ProblemSeeder,
            ReviewStatusSeeder,
            RightSeeder,
            RoleRightGoalSeeder,
            RoleSeeder,
            ValueTypeSeeder,
        )

        return [
            ProblemSeeder(),
            ReviewStatusSeeder(),
            GoalSeeder(),
            RightSeeder(),
            RoleSeeder(),
            RoleRightGoalSeeder(),
            FloorSeeder(),
            ValueTypeSeeder(),
            EventTypeSeeder(),
            PayloadTypeSeeder(),
            AllowedPayloadSeeder(),
            DashboardTypeSeeder(),
        ]

    def setup_app_arguments(self, settings: Settings) -> dict[str, Any]:
        kwargs = super().setup_app_arguments(settings)
        kwargs["version"] = APP_VERSION
        kwargs["openapi_tags"] = TAGS_METADATA
        return kwargs

    # ── Сегменты конфигурации ────────────────────────────────────────────────

    def setup_middlewares(self, app: FastAPI, settings: Settings) -> None:
        if settings.server.cors:
            app.add_middleware(
                CORSMiddleware,  # type: ignore[arg-type]
                allow_origins=settings.allowed_hosts,
                allow_methods=settings.allowed_methods,
                allow_headers=settings.allowed_headers,
                allow_credentials=settings.allow_credentials,
            )
        if settings.server.compression and settings.server.compression.enable:
            app.add_middleware(
                GZipMiddleware,  # type: ignore[arg-type]
                minimum_size=settings.server.compression.minimum_size,
            )

    def setup_routers(self, app: FastAPI) -> None:
        # Состояние привязано к приложению ДО роутеров: guard-зависимости
        # читают его в момент обработки запроса, и оно должно быть на месте.
        app.state.app_state = AppState()

        app.include_router(get.router)
        app.include_router(stat.router)
        app.include_router(review.router)
        app.include_router(check.router)
        app.include_router(auth.router)
        app.include_router(graphql_router, prefix="/api/graphql", tags=["graphql"])
        app.include_router(jobs.router)
        app.include_router(free_aud.router)
        app.include_router(nav.router)
        app.include_router(admin.router)

    def setup_static_files(self, app: FastAPI, settings: Settings) -> None:
        base_static = settings.static_files
        directories: List[str | LiteralString | bytes] = [
            path.join(base_static, "images"),
            path.join(base_static, "auditories"),
            path.join(base_static, "plans"),
            path.join(base_static, "thumbnails"),
        ]
        for directory in directories:
            if not path.exists(directory):
                makedirs(directory)

        if settings.server.static and settings.server.static.files:
            for spa_config in settings.server.static.files:
                fr_dir = Path(spa_config.path)

                if fr_dir.is_absolute():
                    fr_dir = fr_dir.resolve()
                else:
                    fr_dir = (base_static / fr_dir).resolve()

                if not path.exists(fr_dir):
                    logger.warning(
                        f"⚠️ Директория фронтенда не найдена: {fr_dir}. "
                        f"Пропускаем монтирование по пути {fr_dir}"
                    )
                    continue

                if spa_config.fallback:
                    static = SPAStaticFiles(
                        directory=str(fr_dir),
                        html=True,
                        fallback_to=spa_config.fallback_to,
                    )
                else:
                    static = StaticFiles(directory=fr_dir, html=True)

                app.mount(spa_config.mount, static, spa_config.name)
                logger.info(
                    f"✅ Смонтирован SPA фронтенд: {spa_config.mount} -> {fr_dir}"
                )

    def setup_exception_handlers(self, app: FastAPI) -> None:
        @app.exception_handler(SQLAlchemyError)
        async def sqlalchemy_exception_handler(_, _exc: SQLAlchemyError):
            return JSONResponse(
                status_code=500, content={"status": "Internal server error"}
            )

        @app.exception_handler(LookupException)
        async def lookup_exception_handler(_, exc: LookupException):
            return JSONResponse(status_code=404, content={"status": str(exc)})

        @app.exception_handler(HTTPException)
        async def http_exception_handler(_: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.detail}
            )

    # ── Lifespan ─────────────────────────────────────────────────────────────

    async def on_startup(self, app: FastAPI, settings: Settings) -> AppLifespanState:
        init_database(settings)

        state: AppState = app.state.app_state

        try:
            loaded = review_rate_limiter.load_bans(state, settings)
            if loaded > 0:
                logger.info(
                    "Loaded %d banned users from %s", loaded, settings.static_files
                )
        except Exception as e:
            logger.warning("Could not load banned users: %s", e)

        jobs_config = self._resolve_jobs_config(settings)

        job_manager = JobManager(
            static_path=settings.static_files,
            queue_type=jobs_config.queue,
            queue_db=jobs_config.url,
            state=state,
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
