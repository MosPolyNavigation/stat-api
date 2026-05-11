import logging

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI

from app.config import Settings, load_settings
from app.hooks import BaseHooks
from app.helpers.seeder import apply_seeding
from app.jobs import AppLifespanState

logger = logging.getLogger(__name__)


class AppFactory:
    """
    Фабрика FastAPI-приложений на основе BaseHooks.

    В отличие от прежней схемы (app = FastAPI(...) на уровне модуля), создание
    инстанса откладывается до явного вызова __call__. Это убирает сайд-эффекты
    при `import app` и позволяет тестам собирать приложение с собственным набором
    хуков и настроек.
    """

    def __init__(self, hooks: BaseHooks):
        self.hooks = hooks

    def __call__(self, settings: Optional[Settings] = None) -> FastAPI:
        cfg = settings or load_settings()
        cfg = self.hooks.on_config_loaded(cfg)
        self._cfg = cfg
        
        app_kwargs = self.hooks.setup_app_arguments(cfg)

        @asynccontextmanager
        async def lifespan(application: FastAPI) -> AsyncGenerator[AppLifespanState, None]:
            lifespan_state = await self.hooks.on_startup(application, cfg)

            if getattr(cfg.database, "auto_seed", False):
                seeders = self.hooks.setup_seeders()
                if seeders:
                    await apply_seeding(seeders)

            try:
                yield lifespan_state
            finally:
                await self.hooks.on_shutdown(application, cfg, lifespan_state)

        app = FastAPI(
            lifespan=lifespan,
            **app_kwargs
        )
        app.state.config = cfg
        app.state.hooks = self.hooks

        self.hooks.setup_middlewares(app, cfg)
        self.hooks.setup_routers(app)
        self.hooks.setup_static_files(app, cfg)
        self.hooks.setup_exception_handlers(app)

        return app

    @property
    def cfg(self) -> Settings:
        return self._cfg
