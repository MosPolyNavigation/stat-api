from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI

from app.config import Settings, load_settings
from app.hooks import BaseHooks
from app.jobs import AppLifespanState


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

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[AppLifespanState, None]:
            lifespan_state = await self.hooks.on_startup(app, cfg)
            try:
                yield lifespan_state
            finally:
                await self.hooks.on_shutdown(app, cfg, lifespan_state)

        app = FastAPI(
            lifespan=lifespan,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
        )
        app.state.config = cfg
        app.state.hooks = self.hooks

        self.hooks.setup_middlewares(app, cfg)
        self.hooks.setup_routers(app)
        self.hooks.setup_static_files(app, cfg)
        self.hooks.setup_exception_handlers(app)

        return app
