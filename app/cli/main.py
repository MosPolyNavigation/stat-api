import typer
import uvicorn

from app.default_hooks import DefaultHooks
from app.logging import setup_logging
from app.factory import AppFactory
from app.cli.db import db_cli
from . import CONFIG_ENV_NOTE

setup_logging(level="INFO", use_colors=True)

app_cli = typer.Typer(
    name="stat-api",
    help="🚀 Backend для проекта mospolynavigation",
    add_completion=False,
    no_args_is_help=True,
)


@app_cli.callback()
def root_callback() -> None:
    pass


# 🔌 Подключаем группу db
app_cli.add_typer(db_cli, name="db")


@app_cli.command(
    name="serve", help=f"🌐 Запуск FastAPI-сервера через Uvicorn.{CONFIG_ENV_NOTE}"
)
def serve(
    host: str | None = typer.Option(
        None, help="Хост для привязки (переопределяет config.yaml)"
    ),
    port: int | None = typer.Option(
        None, help="Порт для привязки (переопределяет config.yaml)"
    ),
    reload: bool = typer.Option(False, help="Автоперезагрузка при изменении кода"),
    workers: int = typer.Option(1, help="Количество worker-процессов Uvicorn"),
) -> None:
    app_factory = AppFactory(DefaultHooks())
    app = app_factory()
    cfg = app_factory.cfg
    if host is None:
        host = cfg.server.host
    if port is None:
        port = cfg.server.port
    uvicorn.run(app, host=host, port=port, reload=reload, workers=workers)
