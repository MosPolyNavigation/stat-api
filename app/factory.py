import logging

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Sequence

from fastapi import FastAPI

from app.config import Settings, load_settings
from app.seed.base_seeder import BaseSeeder
from app.hooks import BaseHooks
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
        
        app_kwargs = self.hooks.setup_app_arguments(cfg)

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[AppLifespanState, None]:
            lifespan_state = await self.hooks.on_startup(app, cfg)

            if cfg.database.auto_seed:
                seeders = self.hooks.setup_seeders()
                if seeders:
                    logger.info("🌱 Applying database seeders...")
                    await self._apply_seeding(seeders, cfg)
                    logger.info("✅ Database seeded successfully.")

            try:
                yield lifespan_state
            finally:
                await self.hooks.on_shutdown(app, cfg, lifespan_state)

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
    
    async def _apply_seeding(self, seeders: Sequence["BaseSeeder"], settings: Settings) -> None:
        """Выполняет добавление отсутствующих данных для всех переданных сидеров."""
        from app.database import get_session_maker
        maker = get_session_maker()
        
        # Каждая транзакция изолирована. Если один сидер упадёт, остальные не пострадают.
        async with maker() as session:
            for seeder in seeders:
                await seeder.add_missing(session)
                logger.debug(f"  ↳ {seeder.model.__name__} processed")
            await session.commit()
