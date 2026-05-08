from typing import Type, Any

from fastapi import FastAPI

from app.config import Settings
from app.jobs import AppLifespanState
from app.seed.base_seeder import BaseSeeder


class BaseHooks:
    """
    Контракт сегментов настройки приложения.

    Наследники переопределяют нужные методы. AppFactory вызывает их в фиксированном
    порядке: on_config_loaded → setup_middlewares → setup_routers → setup_static_files →
    setup_exception_handlers, а на запуске/остановке — on_startup / on_shutdown.

    Реализации по умолчанию пустые: можно подключать только нужные сегменты,
    например, в TestHooks отключить on_startup, чтобы не поднимать JobManager.
    """

    def setup_app_arguments(self, settings: Settings) -> dict[Any]:
        kwargs = dict()
        if not settings.server.docs.openapi:
            kwargs["openapi_url"] = None
        if not settings.server.docs.docs:
            kwargs["docs_url"] = None
        if not settings.server.docs.redoc:
            kwargs["redoc_url"] = None
        return kwargs
    
    def setup_seeders(self) -> dict[Type[BaseSeeder]]:
        return []

    def on_config_loaded(self, settings: Settings) -> Settings:
        """Хук обработки настроек после загрузки. Возвращает (возможно изменённые) настройки."""
        return settings

    def setup_middlewares(self, app: FastAPI, settings: Settings) -> None:
        """Регистрация middlewares (CORS, GZip и т. д.)."""
        return None

    def setup_routers(self, app: FastAPI) -> None:
        """Регистрация роутеров через app.include_router(...) и инициализация app.state."""
        return None

    def setup_static_files(self, app: FastAPI, settings: Settings) -> None:
        """Подключение статики через app.mount(...) и создание директорий."""
        return None

    def setup_exception_handlers(self, app: FastAPI) -> None:
        """Регистрация глобальных обработчиков исключений."""
        return None

    async def on_startup(self, app: FastAPI, settings: Settings) -> AppLifespanState:
        """
        Выполняется при старте приложения внутри lifespan.

        Returns:
            AppLifespanState: состояние, которое FastAPI прокинет в request.state.
        """
        return AppLifespanState()  # type: ignore[typeddict-item]

    async def on_shutdown(
        self,
        app: FastAPI,
        settings: Settings,
        state: AppLifespanState,
    ) -> None:
        """Выполняется при остановке приложения. Получает состояние, возвращённое из on_startup."""
        return None
