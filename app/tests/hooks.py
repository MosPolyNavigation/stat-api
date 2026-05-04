from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fastapi import FastAPI

from app.config import Settings
from app.database import override_database
from app.default_hooks import DefaultHooks
from app.jobs import AppLifespanState
from app.routes import auth, check, free_aud, get, graphql, nav, review, stat
from app.state import AppState


class TestHooks(DefaultHooks):
    """
    Hooks для pytest-окружения.

    Отличия от DefaultHooks:
        — override_database(session_maker) вызывается уже в __init__: модули,
          обращающиеся к get_session_maker() до создания TestClient (например,
          фикстура seed-данных), должны работать;
        — set up routers ограничен 8 эндпоинтами (без /api/jobs, /api/admin) —
          совместимо с прежней tests/app.py;
        — статика не монтируется и директории не создаются;
        — on_startup / on_shutdown не запускают JobManager и не пишут банов.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        super().__init__()
        override_database(session_maker)

    def setup_routers(self, app: FastAPI) -> None:
        app.state.app_state = AppState()

        app.include_router(get.router)
        app.include_router(stat.router)
        app.include_router(review.router)
        app.include_router(check.router)
        app.include_router(auth.router)
        app.include_router(graphql.graphql_router, prefix="/api/graphql", tags=["graphql"])
        app.include_router(free_aud.router)
        app.include_router(nav.router)

    def setup_static_files(self, app: FastAPI, settings: Settings) -> None:
        return None

    async def on_startup(self, app: FastAPI, settings: Settings) -> AppLifespanState:
        return AppLifespanState(job_manager=None)  # type: ignore[typeddict-item]

    async def on_shutdown(
        self,
        app: FastAPI,
        settings: Settings,
        state: AppLifespanState,
    ) -> None:
        return None
