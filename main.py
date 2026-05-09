import typer
import uvicorn

from app.default_hooks import DefaultHooks
from app.factory import AppFactory

CONFIG_ENV_NOTE = "\n🌍 STATAPI_CONFIG — путь к YAML-файлу конфигурации (по умолчанию: config.yaml)"

app_cli = typer.Typer(
    name="stat-api",
    help=f"🚀 Backend для проекта mospolynavigation.{CONFIG_ENV_NOTE}",
    add_completion=False,
    no_args_is_help=True,  # ← Показывать справку, если не передана подкоманда
)


# ← Корневой коллбэк: фиксирует структуру "статус → подкоманда"
@app_cli.callback()
def root_callback() -> None:
    """🚀 Backend для mospolynavigation."""
    pass


@app_cli.command(name="serve", help=f"🌐 Запуск FastAPI-сервера через Uvicorn.{CONFIG_ENV_NOTE}")
def serve(
    host: str | None = typer.Option(None, help="Хост для привязки (переопределяет config.yaml)"),
    port: int | None = typer.Option(None, help="Порт для привязки (переопределяет config.yaml)"),
    reload: bool = typer.Option(False, help="Автоперезагрузка при изменении кода"),
    workers: int = typer.Option(1, help="Количество worker-процессов Uvicorn"),
) -> None:
    """Запуск HTTP-сервера."""
    app_factory = AppFactory(DefaultHooks())
    app = app_factory()
    cfg = app_factory.cfg

    final_host: str = host or cfg.server.host
    final_port: int = port or cfg.server.port

    uvicorn.run(app, host=final_host, port=final_port, reload=reload, workers=workers)


if __name__ == "__main__":
    app_cli()
