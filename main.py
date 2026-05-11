import typer
import uvicorn

from app.default_hooks import DefaultHooks
from app.logging import setup_logging
from app.factory import AppFactory
from scripts.db import db_cli
from scripts import CONFIG_ENV_NOTE

setup_logging(level="INFO", use_colors=True)

app_cli = typer.Typer(
    name="stat-api",
    help=f"🚀 Backend для проекта mospolynavigation",
    add_completion=False,
    no_args_is_help=True,
)


@app_cli.callback()
def root_callback() -> None:
    pass


# 🔌 Подключаем группу db
app_cli.add_typer(db_cli, name="db")


@app_cli.command(name="serve", help=f"🌐 Запуск FastAPI-сервера через Uvicorn.{CONFIG_ENV_NOTE}")
def serve(
    host: str | None = typer.Option(None, help="Хост для привязки (переопределяет config.yaml)"),
    port: int | None = typer.Option(None, help="Порт для привязки (переопределяет config.yaml)"),
    reload: bool = typer.Option(False, help="Автоперезагрузка при изменении кода"),
    workers: int = typer.Option(1, help="Количество worker-процессов Uvicorn"),
) -> None:
    app_factory = AppFactory(DefaultHooks())
    app = app_factory()
    cfg = app_factory.cfg
    uvicorn.run(app, host=host or cfg.server.host, port=port or cfg.server.port, reload=reload, workers=workers)


if __name__ == "__main__":
    app_cli()
